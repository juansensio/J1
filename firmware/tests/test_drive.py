import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class FakePin:
    OUT = 1

    def __init__(self, number, mode, value):
        self.number = number


class FakePWM:
    def __init__(self, pin, freq, duty_u16):
        self.pin = pin
        self.duty = duty_u16
        self.history = [duty_u16]

    def duty_u16(self, value):
        self.duty = value
        self.history.append(value)


class DriveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        machine = types.ModuleType("machine")
        machine.Pin = FakePin
        machine.PWM = FakePWM
        root = Path(__file__).parents[1] / "src"
        with patch.dict(sys.modules, {"machine": machine}):
            motor_spec = importlib.util.spec_from_file_location(
                "src.motor", root / "motor.py"
            )
            cls.motor_module = importlib.util.module_from_spec(motor_spec)
            motor_spec.loader.exec_module(cls.motor_module)
            with patch.dict(sys.modules, {"src.motor": cls.motor_module}):
                drive_spec = importlib.util.spec_from_file_location(
                    "src.drive_under_test", root / "drive.py"
                )
                drive_module = importlib.util.module_from_spec(drive_spec)
                drive_spec.loader.exec_module(drive_module)
                cls.drive_module = drive_module
                cls.Drive = drive_module.Drive

    def setUp(self):
        self.now = 0
        ticks = patch.object(
            self.drive_module.time, "ticks_ms", side_effect=lambda: self.now, create=True
        )
        difference = patch.object(
            self.drive_module.time, "ticks_diff", side_effect=lambda a, b: a - b,
            create=True,
        )
        ticks.start()
        difference.start()
        self.addCleanup(ticks.stop)
        self.addCleanup(difference.stop)

    def test_motor_speed_controls_pwm_direction_and_stop(self):
        motor = self.motor_module.Motor(2, 1)
        motor.drive(50)
        self.assertEqual((motor.in1.duty, motor.in2.duty), (32767, 0))
        motor.drive(-100)
        self.assertEqual((motor.in1.duty, motor.in2.duty), (0, 65535))
        motor.stop()
        self.assertEqual((motor.in1.duty, motor.in2.duty), (0, 0))

    def test_drive_sets_each_side_and_stops_all_motors(self):
        drive = self.Drive(((2, 1), (41, 42)), ((48, 45), (21, 47)))
        drive.drive(100, -25)
        for motor in drive.left_motors:
            self.assertEqual((motor.in1.duty, motor.in2.duty), (65535, 0))
        for motor in drive.right_motors:
            self.assertEqual((motor.in1.duty, motor.in2.duty), (0, 16383))
        drive.stop()
        for motor in drive.motors:
            self.assertEqual((motor.in1.duty, motor.in2.duty), (0, 0))

    def test_invalid_speed_leaves_motor_outputs_unchanged(self):
        drive = self.Drive(((2, 1),), ((48, 45),))
        with self.assertRaises(ValueError):
            drive.drive(50, 101)
        for motor in drive.motors:
            self.assertEqual((motor.in1.duty, motor.in2.duty), (0, 0))

    def test_watchdog_stops_at_750_ms(self):
        drive = self.Drive(((2, 1),), ((48, 45),))
        drive.drive(30, -30)
        self.now = 749
        drive.check_watchdog()
        self.assertNotEqual(drive.left_motors[0].in1.duty, 0)
        self.now = 750
        drive.check_watchdog()
        self.assertIsNone(drive.last_drive_ms)
        for motor in drive.motors:
            self.assertEqual((motor.in1.duty, motor.in2.duty), (0, 0))

    def test_each_drive_renews_watchdog(self):
        drive = self.Drive(((2, 1),), ((48, 45),))
        drive.drive(30, 30)
        self.now = 500
        drive.drive(20, 20)
        self.now = 1249
        drive.check_watchdog()
        self.assertNotEqual(drive.left_motors[0].in1.duty, 0)
        self.now = 1250
        drive.check_watchdog()
        self.assertEqual(drive.left_motors[0].in1.duty, 0)


if __name__ == "__main__":
    unittest.main()
