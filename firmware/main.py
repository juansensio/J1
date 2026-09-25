import wifi_config
import time
from src.server import BadRequest, Server
from src.logger import configure, get_logger
from src.drive import Drive

# configure logger
host = getattr(wifi_config, "LOG_HOST", None)
port = getattr(wifi_config, "LOG_PORT", 9999)
configure(host, port)
log = get_logger("main")

# car drive setup
LEFT_PINS = ((2, 1), (41, 42))  # rear left, front left
RIGHT_PINS = ((48, 45), (21, 47))  # front right, rear right
drive = Drive(LEFT_PINS, RIGHT_PINS)

# add endpoints to the server
server = Server(
    wifi_config.WIFI_SSID, wifi_config.WIFI_PASSWORD, wifi_config.CONTROL_TOKEN
)


@server.get("/drive")
def drive_route(request):
    try:
        left = int(request.args["left"])
        right = int(request.args["right"])
    except (KeyError, ValueError):
        raise BadRequest("left and right must be integers from -100 to 100")
    if not -100 <= left <= 100 or not -100 <= right <= 100:
        raise BadRequest("left and right must be integers from -100 to 100")
    drive.drive(left, right)
    return "Driving left=%d right=%d" % (left, right)


@server.get("/stop")
def stop_route(request):
    drive.stop()
    return "Stopped"


@server.get("/health")
def health(request):
    return "OK"


# control loop
try:
    while True:
        try:
            server.run()
        except OSError as exc:
            drive.stop()
            log.error("Network error:", exc)
            time.sleep(2)
finally:
    drive.stop()
    server.close()
    log.info("Server closed")
