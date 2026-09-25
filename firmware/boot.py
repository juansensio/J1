from machine import Pin
import network
import time
import webrepl

import wifi_config

from src.buzzer import buzz
# from src.logger import configure, get_logger

# # configure logger
# host = getattr(wifi_config, "LOG_HOST", None)
# port = getattr(wifi_config, "LOG_PORT", 9999)
# configure(host, port)
# log = get_logger("boot")

# # connect to wifi
# wlan = network.WLAN(network.WLAN.IF_STA)
# wlan.active(True)
# if not wlan.isconnected():
#     wlan.connect(wifi_config.WIFI_SSID, wifi_config.WIFI_PASSWORD)
#     started = time.ticks_ms()
#     while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), started) < 15000:
#         time.sleep_ms(100)
# if wlan.isconnected():
#     log.info("Robot IP:", wlan.ifconfig()[0])
# else:
#     log.warning("Wi-Fi unavailable at boot; main.py will retry")

# flash led and buzz
led = Pin(38, Pin.OUT, value=0)
buzzer = Pin(37, Pin.OUT, value=0)
# log.info("LED on; buzzer on at 2 kHz")
led.on()
buzz(buzzer)
led.off()
# log.info("Boot complete; LED and buzzer off")

# start webrepl
# try:
#     webrepl.start()
# except (ImportError, OSError) as exc:
#     log.warning("WebREPL unavailable:", exc)
