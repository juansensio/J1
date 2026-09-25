import time
from urllib.request import Request, urlopen

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist

from bridge.kinematics import twist_to_wheels


class Bridge(Node):
    def __init__(self):
        super().__init__("bridge")
        self.declare_parameter("robot_host", "")
        self.declare_parameter("robot_token", "")
        self.declare_parameter("command_timeout", 0.5)
        self.robot_host = self.get_parameter("robot_host").value
        self.robot_token = self.get_parameter("robot_token").value
        self.command_timeout = self.get_parameter("command_timeout").value
        if not self.robot_host or not self.robot_token:
            raise ValueError("robot_host and robot_token ROS parameters are required")
        if self.command_timeout <= 0:
            raise ValueError("command_timeout must be positive")

        self.left = 0
        self.right = 0
        self.last_cmd_time = None
        self.stopped = True

        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,  # if the publisher is not reliable, the subscriber will not receive the messages
        )
        self.subscription = self.create_subscription(
            Twist,
            "/cmd_vel",
            self.callback,
            qos,
        )
        self.create_timer(0.1, self.tick)
        self.get_logger().info(
            f"Bridge ready: /cmd_vel -> http://{self.robot_host} "
            f"(timeout={self.command_timeout:.2f}s)"
        )

    def callback(self, message):
        left, right = twist_to_wheels(
            message.linear.x,
            message.angular.z,
        )
        if self.stopped or (left, right) != (self.left, self.right):
            self.get_logger().info(f"/cmd_vel -> left={left} right={right}")
        self.left, self.right = left, right
        self.last_cmd_time = time.monotonic()
        self.stopped = False

    def tick(self):
        if self.last_cmd_time is None or self.stopped:
            return

        if time.monotonic() - self.last_cmd_time < self.command_timeout:
            path = f"/drive?left={self.left}&right={self.right}"
        else:
            path = "/stop"

        request = Request(
            f"http://{self.robot_host}{path}",
            headers={"X-Robot-Token": self.robot_token},
        )
        try:
            with urlopen(request, timeout=0.25) as response:
                response.read()
                self.get_logger().info(f"HTTP {path} -> {response.status}")
        except OSError as exc:
            self.get_logger().warning(f"Robot HTTP request failed: {exc}")
            return

        if path == "/stop":
            self.stopped = True


def main(args=None):
    rclpy.init(args=args)
    node = Bridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
