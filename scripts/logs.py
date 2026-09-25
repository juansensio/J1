"""Print UDP log messages sent by J0."""

import argparse
import datetime
import socket
import sys


def show(message):
    # A WebREPL session can leave a terminal in raw mode, where LF alone does
    # not return the cursor to column zero.
    ending = "\r\n" if sys.stdout.isatty() else "\n"
    sys.stdout.write(message + ending)
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=9999)
    args = parser.parse_args()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
        listener.bind(("0.0.0.0", args.port))
        show("Listening for J0 logs on UDP port %d" % args.port)
        while True:
            payload, address = listener.recvfrom(2048)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            message = payload.decode("utf-8", "replace")
            show("%s %s %s" % (timestamp, address[0], message))


if __name__ == "__main__":
    main()
