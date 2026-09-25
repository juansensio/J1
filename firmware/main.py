import wifi_config
import time
from src.server import Server
from src.logger import configure, get_logger

host = getattr(wifi_config, "LOG_HOST", None)
port = getattr(wifi_config, "LOG_PORT", 9999)
configure(host, port)
log = get_logger("main")

server = None
try:
    server = Server(
        wifi_config.WIFI_SSID, wifi_config.WIFI_PASSWORD, wifi_config.CONTROL_TOKEN
    )
    while True:
        try:
            server.run()
        except OSError as exc:
            log.error("Network error:", exc)
            time.sleep(2)
finally:
    if server is not None:
        server.close()
    log.info("Server closed")
