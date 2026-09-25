## J1

Evolution of https://github.com/juansensio/J0, a 4-wheeled robot, now adding ROS 2.

**Directory Structure**

- **docs/** — Project documentation
- **firmware/** — ESP32 / MicroPython firmware
- **ros2_ws/** — ROS 2 Jazzy workspace

ROS 2 sends commands to the robot via the `/cmd_vel` topic. The robot then drives based on the commands.