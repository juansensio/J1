import io
import unittest
from unittest.mock import patch

from scripts import logs


class TerminalOutputTest(unittest.TestCase):
    def test_terminal_lines_return_to_column_zero(self):
        output = io.StringIO()
        output.isatty = lambda: True
        with patch.object(logs.sys, "stdout", output):
            logs.show("first")
            logs.show("second")
        self.assertEqual(output.getvalue(), "first\r\nsecond\r\n")

    def test_redirected_output_uses_plain_newlines(self):
        output = io.StringIO()
        with patch.object(logs.sys, "stdout", output):
            logs.show("first")
        self.assertEqual(output.getvalue(), "first\n")
