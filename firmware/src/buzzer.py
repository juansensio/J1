from machine import Pin, PWM
import time


def buzz(pin):
    buzzer = PWM(pin, freq=2000, duty_u16=32768)
    time.sleep(1)
    buzzer.duty_u16(0)
    buzzer.deinit()
    pin.init(Pin.OUT, value=0)
