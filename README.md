## J1

Evolution of https://github.com/juansensio/J0, a 4-wheeled robot, now adding ROS 2.

**Directory Structure**

- **docs/** — Project documentation
- **firmware/** — ESP32 / MicroPython firmware
- **ros2_ws/** — ROS 2 Jazzy workspace

ROS 2 sends commands to the robot via the `/cmd_vel` topic. The robot then drives based on the commands.

## ROS to robot control

The `bridge` node subscribes to `/cmd_vel`. Every 100 ms it sends the latest
wheel speeds to `GET /drive?left=X&right=Y`, with `X-Robot-Token` in the HTTP
header. If no command arrives for 0.5 seconds, it sends `GET /stop` once.
The ESP32 also stops its motors after 750 ms without a `/drive` request, even
if the bridge process disappears.

Set `ROBOT_HOST` (IP address or hostname, without `http://`) and `ROBOT_TOKEN`
(the ESP32 `CONTROL_TOKEN`) in the project root `.env`. Docker Compose passes
them to the ROS container. The bridge also accepts the ROS parameter
`command_timeout` (seconds, default `0.5`).

With the wheels lifted off the ground, start the ESP32, run `make run` and
`make bash`, then run in the ROS 2 container:

```bash
cd /root/ros2_ws
colcon build --packages-select bridge
source install/setup.zsh
curl --fail --silent --show-error \
  -H "X-Robot-Token: $ROBOT_TOKEN" \
  "http://$ROBOT_HOST/health"
ros2 run bridge bridge --ros-args \
  -p robot_host:="$ROBOT_HOST" \
  -p robot_token:="$ROBOT_TOKEN"
```

In a second ROS 2 terminal, source the same setup file and publish a forward
command:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.0}}"
```

Expect both sides to run at 50%. Stop the publisher and check that `/stop` is
sent on the next 100 ms timer tick after the 500 ms timeout. Then repeat the
movement and terminate the bridge; the ESP32 watchdog should stop the motors
within 750 ms of its last `/drive` request. The ESP32 request logs show the
`/drive` and `/stop` calls and watchdog expiry.

## Mando web

Rebuild the Docker image after changing the Dockerfile. Start the HTML web
server, then start rosbridge and the ROS-to-ESP32 node separately with the wheels
lifted off the ground:

```bash
make build
make client
make bridge
```

`make client` starts only the static web server. `make bridge` builds the ROS
package, then starts rosbridge and the node that forwards `/cmd_vel` to the ESP32. Both commands
can be run again without starting duplicate processes. Run `make logs` in a
second terminal to see `/cmd_vel`, HTTP
`/drive`, `/stop`, and errors from the bridge.

Open [http://192.168.1.96:8080](http://192.168.1.96:8080) on a phone connected to the same Wi-Fi as the
Mac. Hold an arrow to publish `/cmd_vel` at 10 Hz; releasing it or pressing
STOP publishes a zero `Twist`. The page shows WebSocket status and outgoing
`Twist` messages. The page loads
roslibjs from jsDelivr, so the phone also needs Internet access. Ports 8080
and 9090 are intended only for a trusted local network; do not forward them
to the Internet.
