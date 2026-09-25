from machine import Pin
import network
import time
import webrepl

import wifi_config

from src.buzzer import buzz
from src.logger import configure, get_logger

# flash led and buzz
led = Pin(38, Pin.OUT, value=0)
buzzer = Pin(37, Pin.OUT, value=0)
led.on()
buzz(buzzer)

# configure logger
host = getattr(wifi_config, "LOG_HOST", None)
port = getattr(wifi_config, "LOG_PORT", 9999)
configure(host, port)
log = get_logger("boot")

# connect to wifi
# Logger will not work until wifi is connected !!!
wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(wifi_config.WIFI_SSID, wifi_config.WIFI_PASSWORD)
    started = time.ticks_ms()
    while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), started) < 15000:
        time.sleep_ms(100)
if wlan.isconnected():
    log.info("Robot IP:", wlan.ifconfig()[0])
else:
    log.warning("Wi-Fi unavailable at boot; main.py will retry")

# start webrepl
try:
    webrepl.start()
    log.info("WebREPL started")
    led.off()
except (ImportError, OSError) as exc:
    log.warning("WebREPL unavailable:", exc)
