from .motor import Motor
from src.logger import get_logger
import time

log = get_logger("Drive")


class Drive:
    WATCHDOG_MS = 750  # 750ms is the maximum time between drive commands. Otherwise the robot will stop.

    def __init__(self, left_pins, right_pins):
        self.left_motors = [Motor(*pins) for pins in left_pins]
        self.right_motors = [Motor(*pins) for pins in right_pins]
        self.motors = self.left_motors + self.right_motors
        self.last_drive_ms = None
        log.info(
            f"Drive initialized with left motors: {self.left_motors} and right motors: {self.right_motors}"
        )

    def drive(self, left, right):
        if not all(
            isinstance(speed, int) and -100 <= speed <= 100 for speed in (left, right)
        ):
            raise ValueError("Drive speeds must be integers from -100 to 100")
        log.info(f"Driving left: {left}, right: {right}")
        for motor in self.left_motors:
            motor.drive(left)
        for motor in self.right_motors:
            motor.drive(right)
        self.last_drive_ms = time.ticks_ms()

    def check_watchdog(self):
        if (
            self.last_drive_ms is not None
            and time.ticks_diff(time.ticks_ms(), self.last_drive_ms) >= self.WATCHDOG_MS
        ):
            log.warning("Drive watchdog expired")
            self.stop()

    def stop(self):
        self.last_drive_ms = None
        for motor in self.motors:
            motor.stop()
        log.info("Drive stopped")
