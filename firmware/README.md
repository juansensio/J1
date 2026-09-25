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

### Robot control

- `GET /drive?left=X&right=Y` sets the left and right motor speeds independently. Both values are required integers from `-100` to `100`: positive drives the motor's first input, negative drives its second input, and zero stops that side.
- `GET /stop` stops all four motors.
- `GET /health` returns `OK`.

The motor pin pairs are configured in `main.py`. Each `/drive` command renews a 750 ms watchdog; if no new drive command arrives in time, all motors stop. `/stop` and network errors also stop them. Send the `X-Robot-Token` header with each request.

To watch request logs, run `make logs` in one terminal and `make test-endpoints` or `make test-drive` in another. The scripts read `ROBOT_HOST` and `ROBOT_TOKEN` from `.env` or the environment and send `/stop` when they exit.

For a short movement test, run `make test-drive`. It ramps both sides up and down for forward and reverse movement, then ramps into left and right turns before stopping.

To verify the watchdog itself, run `make test-watchdog` while watching the logs. It sends one `/drive`, waits 1.2 seconds without refreshing it, then checks `/health`. Expect `Drive watchdog expired` before the script's final `/stop` request. Interrupting a movement script sends `/stop` immediately, so that does not exercise the watchdog.
