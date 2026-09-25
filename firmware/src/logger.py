"""Small console and best-effort UDP logger for MicroPython."""

import socket


_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
_host = None
_port = 9999
_level = 20
_socket = None


def _close_socket():
    global _socket
    if _socket is not None:
        try:
            _socket.close()
        except OSError:
            pass
        _socket = None


def configure(host=None, port=9999, level="INFO"):
    """Set the Mac's IP and UDP port; omit host for console-only logging."""
    global _host, _port, _level
    if level not in _LEVELS:
        raise ValueError("invalid log level: " + str(level))
    if not 1 <= port <= 65535:
        raise ValueError("invalid log port")
    _close_socket()
    _host = host or None
    _port = port
    _level = _LEVELS[level]


class Logger:
    def __init__(self, name):
        self.name = name

    def _write(self, level, *parts):
        global _socket
        if _LEVELS[level] < _level:
            return
        message = "%s %s: %s" % (level, self.name, " ".join(str(p) for p in parts))
        print(message)
        if _host is None:
            return
        try:
            if _socket is None:
                _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                _socket.setblocking(False)
            _socket.sendto(message.encode()[:512], (_host, _port))
        except OSError:
            # Logging must never interrupt robot control. Retry on the next log.
            _close_socket()

    def debug(self, *parts):
        self._write("DEBUG", *parts)

    def info(self, *parts):
        self._write("INFO", *parts)

    def warning(self, *parts):
        self._write("WARNING", *parts)

    def error(self, *parts):
        self._write("ERROR", *parts)


def get_logger(name):
    return Logger(name)
