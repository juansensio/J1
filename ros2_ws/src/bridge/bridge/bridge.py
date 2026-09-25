import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from geometry_msgs.msg import Twist


class Bridge(Node):
    def __init__(self):
        super().__init__("bridge")
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

    def callback(self, message):
        self.get_logger().info(
            f"Raw twist: {message.linear.x:.2f} {message.angular.z:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = Bridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
