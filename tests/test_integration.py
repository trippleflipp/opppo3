import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import main as sh


def _write_tmp(content, encoding="utf-8-sig"):
    f = tempfile.NamedTemporaryFile(
        mode="w", encoding=encoding, suffix=".txt", delete=False
    )
    with f:
        f.write(content)
    return f.name


class TestProcessFile(unittest.TestCase):
    def test_valid_file(self):
        path = _write_tmp(
            'ADD LAMP "Xiaomi" 10 E27\n'
            'ADD SOCKET "TP-Link" 3500\n'
            'PRINT\n'
        )
        try:
            home = sh.SmartHome()
            with redirect_stdout(io.StringIO()):
                home.process_file(path)
            self.assertEqual(len(home.devices), 2)
        finally:
            os.unlink(path)

    def test_error_does_not_stop_processing(self):
        path = _write_tmp(
            'ADD LAMP "Xiaomi" abc E27\n'   # ошибка в одной строке
            'ADD SOCKET "TP-Link" 3500\n'   # следующая строка валидна
        )
        try:
            home = sh.SmartHome()
            buf = io.StringIO()
            with redirect_stdout(buf):
                home.process_file(path)
            self.assertIn("Ошибка", buf.getvalue())
            self.assertEqual(len(home.devices), 1)
            self.assertIsInstance(home.devices[0], sh.SmartSocket)
        finally:
            os.unlink(path)

    def test_bom_is_stripped(self):
        path = _write_tmp('\ufeffADD SOCKET "TP-Link" 3500\n', encoding="utf-8")
        try:
            home = sh.SmartHome()
            with redirect_stdout(io.StringIO()):
                home.process_file(path)
            self.assertEqual(len(home.devices), 1)
        finally:
            os.unlink(path)


class TestMain(unittest.TestCase):
    def test_no_args_returns_1(self):
        with patch.object(sys, "argv", ["prog"]):
            self.assertEqual(sh.main(), 1)

    def test_valid_file_returns_0(self):
        path = _write_tmp('ADD LAMP "Xiaomi" 10 E27\n')
        try:
            with patch.object(sys, "argv", ["prog", path]), \
                 redirect_stdout(io.StringIO()):
                self.assertEqual(sh.main(), 0)
        finally:
            os.unlink(path)

    def test_missing_file_returns_1(self):
        with patch.object(sys, "argv", ["prog", "/no/such/file.txt"]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                result = sh.main()
            self.assertEqual(result, 1)
            self.assertIn("Не удалось прочитать файл", buf.getvalue())


if __name__ == "__main__":
    unittest.main()