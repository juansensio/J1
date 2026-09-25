from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import Mock, patch


class StopMain(Exception):
    pass


class FakeWLAN:
    IF_STA = 0

    def __init__(self, interface):
        pass


class FakeConnection:
    def __init__(self, path):
        self.request = (
            "GET %s HTTP/1.1\r\nX-Robot-Token: secret\r\n\r\n" % path
        ).encode()
        self.response = b""

    def recv(self, size):
        return self.request

    def sendall(self, data):
        self.response += data


class EndpointTest(unittest.TestCase):
    def setUp(self):
        wifi = types.ModuleType("wifi_config")
        wifi.WIFI_SSID = "test"
        wifi.WIFI_PASSWORD = "test"
        wifi.CONTROL_TOKEN = "secret"
        network = types.ModuleType("network")
        network.WLAN = FakeWLAN
        machine = types.ModuleType("machine")
        drive_module = types.ModuleType("src.drive")
        self.drive = Mock()
        drive_module.Drive = Mock(return_value=self.drive)
        with patch.dict(sys.modules, {
            "wifi_config": wifi,
            "network": network,
            "machine": machine,
            "src.drive": drive_module,
        }):
            from src.server import Server

            main = Path(__file__).parents[1] / "main.py"
            with patch.object(Server, "run", autospec=True, side_effect=StopMain) as run:
                with self.assertRaises(StopMain):
                    runpy.run_path(str(main), run_name="routes_test")
                self.server = run.call_args.args[0]
        self.drive.reset_mock()  # main.py stops the motors when its loop exits.

    def request(self, path):
        conn = FakeConnection(path)
        self.server._handle(conn)
        return conn.response

    def test_drive_passes_signed_speeds_to_both_sides(self):
        response = self.request("/drive?left=-75&right=50")
        self.assertIn(b"200 OK", response)
        self.assertTrue(response.endswith(b"Driving left=-75 right=50"))
        self.drive.drive.assert_called_once_with(-75, 50)

    def test_drive_rejects_missing_non_numeric_and_out_of_range_values(self):
        for path in (
            "/drive?left=10",
            "/drive?left=abc&right=10",
            "/drive?left=101&right=10",
        ):
            with self.subTest(path=path):
                self.assertIn(b"400 Bad Request", self.request(path))
        self.drive.drive.assert_not_called()

    def test_stop_and_health(self):
        self.assertTrue(self.request("/stop").endswith(b"Stopped"))
        self.drive.stop.assert_called_once_with()
        self.assertTrue(self.request("/health").endswith(b"OK"))


if __name__ == "__main__":
    unittest.main()
