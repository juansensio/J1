"""Check ROS command timing and the HTTP protocol without ROS hardware."""

import importlib
import sys
import types
from unittest.mock import Mock, patch


def load_bridge():
    """Import the bridge with a small stand-in for the ROS node API."""
    rclpy = types.ModuleType("rclpy")
    node = types.ModuleType("rclpy.node")
    qos = types.ModuleType("rclpy.qos")
    geometry = types.ModuleType("geometry_msgs")
    geometry_msg = types.ModuleType("geometry_msgs.msg")

    class Node:
        def __init__(self, name):
            self.name = name
            self.parameters = {
                "robot_host": "robot.local",
                "robot_token": "secret",
                "command_timeout": 0.5,
            }
            self.logger = Mock()

        def declare_parameter(self, name, default):
            self.parameters.setdefault(name, default)

        def get_parameter(self, name):
            return types.SimpleNamespace(value=self.parameters[name])

        def create_subscription(self, *args):
            return args

        def create_timer(self, interval, callback):
            self.timer = (interval, callback)

        def get_logger(self):
            return self.logger

    node.Node = Node
    qos.QoSProfile = lambda **kwargs: kwargs
    qos.ReliabilityPolicy = types.SimpleNamespace(RELIABLE=1)
    geometry_msg.Twist = type("Twist", (), {})
    with patch.dict(sys.modules, {
        "rclpy": rclpy,
        "rclpy.node": node,
        "rclpy.qos": qos,
        "geometry_msgs": geometry,
        "geometry_msgs.msg": geometry_msg,
    }):
        sys.modules.pop("bridge.bridge", None)
        return importlib.import_module("bridge.bridge").Bridge


def test_drive_then_one_stop_after_timeout():
    bridge_module = load_bridge()
    bridge = bridge_module()
    message = types.SimpleNamespace(
        linear=types.SimpleNamespace(x=0.5),
        angular=types.SimpleNamespace(z=0.0),
    )
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)

    with patch("bridge.bridge.time.monotonic", return_value=100.0), patch(
        "bridge.bridge.urlopen", return_value=response
    ) as send:
        bridge.callback(message)
        assert send.call_count == 0
        assert (bridge.left, bridge.right, bridge.last_cmd_time, bridge.stopped) == (
            50, 50, 100.0, False
        )
        assert bridge.timer == (0.1, bridge.tick)

        bridge.tick()
        request = send.call_args.args[0]
        assert request.full_url == "http://robot.local/drive?left=50&right=50"
        assert request.get_header("X-robot-token") == "secret"
        assert send.call_args.kwargs["timeout"] == 0.25

    with patch("bridge.bridge.time.monotonic", return_value=100.5), patch(
        "bridge.bridge.urlopen", return_value=response
    ) as send:
        bridge.tick()
        bridge.tick()
        assert send.call_count == 1
        assert send.call_args.args[0].full_url == "http://robot.local/stop"
        assert bridge.stopped


def test_failed_stop_retries_until_acknowledged():
    bridge = load_bridge()()
    bridge.last_cmd_time = 1.0
    bridge.stopped = False
    with patch("bridge.bridge.time.monotonic", return_value=2.0), patch(
        "bridge.bridge.urlopen", side_effect=OSError("offline")
    ) as send:
        bridge.tick()
        bridge.tick()
        assert send.call_count == 2
        assert not bridge.stopped
        assert bridge.logger.warning.call_count == 2


def test_new_command_resumes_after_stop():
    bridge = load_bridge()()
    message = types.SimpleNamespace(
        linear=types.SimpleNamespace(x=-0.25),
        angular=types.SimpleNamespace(z=0.0),
    )
    with patch("bridge.bridge.time.monotonic", return_value=10.0), patch(
        "bridge.bridge.urlopen"
    ) as send:
        bridge.tick()
        send.assert_not_called()
        bridge.callback(message)
        bridge.tick()
        assert send.call_args.args[0].full_url == (
            "http://robot.local/drive?left=-25&right=-25"
        )

    with patch("bridge.bridge.time.monotonic", return_value=10.6), patch(
        "bridge.bridge.urlopen"
    ) as send:
        bridge.tick()
        assert bridge.stopped
        assert send.call_args.args[0].full_url == "http://robot.local/stop"

    with patch("bridge.bridge.time.monotonic", return_value=11.0), patch(
        "bridge.bridge.urlopen"
    ) as send:
        bridge.callback(message)
        bridge.tick()
        assert not bridge.stopped
        assert send.call_args.args[0].full_url == (
            "http://robot.local/drive?left=-25&right=-25"
        )
