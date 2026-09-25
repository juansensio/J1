from machine import Pin, PWM
from src.logger import get_logger

log = get_logger("Motor")


class Motor:
    def __init__(self, in1: int, in2: int):
        self.in1 = PWM(Pin(in1, Pin.OUT, value=0), freq=2000, duty_u16=0)
        self.in2 = PWM(Pin(in2, Pin.OUT, value=0), freq=2000, duty_u16=0)
        log.info(f"Motor initialized with in1: {in1} and in2: {in2}")

    def stop(self):
        self.in1.duty_u16(0)
        self.in2.duty_u16(0)
        log.info("Motor stopped")

    def drive(self, speed):
        if not isinstance(speed, int) or not -100 <= speed <= 100:
            raise ValueError("Motor speed must be an integer from -100 to 100")
        duty = abs(speed) * 65535 // 100
        log.info(f"Driving motor with speed: {speed}, duty: {duty}")
        # Clear both inputs before changing direction.
        self.in1.duty_u16(0)
        self.in2.duty_u16(0)
        if speed > 0:
            self.in1.duty_u16(duty)
        elif speed < 0:
            self.in2.duty_u16(duty)
