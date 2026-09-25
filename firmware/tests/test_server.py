import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class FakeConnection:
    def __init__(self, request):
        self.request = request
        self.response = b""

    def recv(self, size):
        return self.request

    def sendall(self, data):
        self.response += data


class ServerRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = patch.dict(sys.modules, {
            "machine": types.ModuleType("machine"),
            "network": types.ModuleType("network"),
        })
        cls.modules.start()
        path = Path(__file__).parents[1] / "src" / "server.py"
        spec = importlib.util.spec_from_file_location("server_routes_test", path)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    @classmethod
    def tearDownClass(cls):
        cls.modules.stop()

    def setUp(self):
        self.server = object.__new__(self.module.Server)
        self.server.token = "secret"
        self.server.routes = []

    def request(self, path, token="secret"):
        data = ("GET %s HTTP/1.1\r\nX-Robot-Token: %s\r\n\r\n" % (path, token)).encode()
        conn = FakeConnection(data)
        self.server._handle(conn)
        return conn.response

    def test_registered_route_receives_path_and_query_parameters(self):
        @self.server.get("/move/<direction>/<int:seconds>")
        def move(request, direction, seconds):
            return "%s %d %s" % (direction, seconds, request.args["speed"])

        response = self.request("/move/forward/2?speed=fast")
        self.assertIn(b"200 OK", response)
        self.assertTrue(response.endswith(b"forward 2 fast"))

    def test_static_route_wins_and_token_is_required(self):
        @self.server.get("/<name>")
        def variable(request, name):
            return name

        @self.server.get("/status")
        def status(request):
            return "Robot alive"

        self.assertTrue(self.request("/status").endswith(b"Robot alive"))
        self.assertIn(b"403 Forbidden", self.request("/status", "wrong"))
        self.assertIn(b"404 Not Found", self.request("/missing/extra"))

    def test_reset_route_is_reserved(self):
        with self.assertRaises(ValueError):
            self.server.get("/reset")

    def test_failed_handler_returns_error_without_stopping_server(self):
        @self.server.get("/fail")
        def fail(request):
            raise ValueError("bad input")

        with patch.object(self.module.log, "error"):
            self.assertIn(b"500 Internal Server Error", self.request("/fail"))


if __name__ == "__main__":
    unittest.main()
