# Firmware

## Booting

`boot.py` is the boot file that sets up the robot.

1. Led and buzzer are turned on to indicate that the robot is booting.
2. Wifi logger is configured.
3. Wi-Fi is connected.
4. WebREPL is started.

If everything goes well, the led is turned off.

- `src/logger.py` → creates a socket to send logs to a remote server. Needs wifi to be connected.

> Start `scripts/logs.py` in a terminal to see the logs in real time.

## Main

`main.py` is the main file that runs the robot.

1. Wifi logger is configured.
2. Server is initialized
3. Endpoints are defined (flask-style)
4. Server is started. Will listen for commands to control the robot.

- `src/server.py` → starts a socket server that listens for commands to control the robot. Parses inputs and returns responses.



### HTTP routes

Define GET routes in `main.py` before calling `server.run()`:

```python
@server.get("/move/<direction>")
def move(request, direction):
    seconds = int(request.args.get("seconds", "1"))
    # Control the robot here.
    return "Moving " + direction
```

`/move/forward?seconds=2` passes `forward` as `direction` and makes `seconds` available in `request.args`. Use `<int:name>` for an integer path value. Handlers return plain text. All routes require the existing `X-Robot-Token` header. `/reset` remains a built-in route so its response can be sent before the board restarts.