import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src import logger


class LoggerTest(unittest.TestCase):
    def tearDown(self):
        logger.configure()

    def test_console_only_and_level_filter(self):
        logger.configure(level="WARNING")
        output = io.StringIO()
        with redirect_stdout(output):
            log = logger.get_logger("drive")
            log.info("moving")
            log.warning("stopped", 42)
        self.assertEqual(output.getvalue(), "WARNING drive: stopped 42\n")

    def test_udp_message_and_reuse(self):
        logger.configure("192.168.1.50", 9999)
        with patch.object(logger.socket, "socket") as socket_factory:
            with redirect_stdout(io.StringIO()):
                log = logger.get_logger("robot")
                log.info("ready")
                log.error("fault", 7)
            self.assertEqual(socket_factory.call_count, 1)
            sock = socket_factory.return_value
            sock.setblocking.assert_called_once_with(False)
            self.assertEqual(sock.sendto.call_args_list[0].args,
                             (b"INFO robot: ready", ("192.168.1.50", 9999)))
            self.assertEqual(sock.sendto.call_args_list[1].args,
                             (b"ERROR robot: fault 7", ("192.168.1.50", 9999)))
            logger.configure()
            sock.close.assert_called_once()

    def test_udp_failure_does_not_stop_logging(self):
        logger.configure("192.168.1.50")
        with patch.object(logger.socket, "socket") as socket_factory:
            sock = socket_factory.return_value
            sock.sendto.side_effect = OSError("network down")
            output = io.StringIO()
            with redirect_stdout(output):
                logger.get_logger("robot").error("fault")
            self.assertEqual(output.getvalue(), "ERROR robot: fault\n")
            sock.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
