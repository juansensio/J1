from .motor import Motor
from src.logger import get_logger

log = get_logger("Drive")


class Drive:
    def __init__(self, left_pins, right_pins):
        self.left_motors = [Motor(*pins) for pins in left_pins]
        self.right_motors = [Motor(*pins) for pins in right_pins]
        self.motors = self.left_motors + self.right_motors
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

    def stop(self):
        for motor in self.motors:
            motor.stop()
        log.info("Drive stopped")
