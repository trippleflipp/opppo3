import math
import unittest

import main as sh


class TestParseNumberSuccess(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(sh.parse_number("42", "power"), 42.0)

    def test_float(self):
        self.assertAlmostEqual(sh.parse_number("3.14", "power"), 3.14)

    def test_negative(self):
        self.assertEqual(sh.parse_number("-5", "temp"), -5.0)

    def test_positive_flag_ok(self):
        self.assertEqual(sh.parse_number("1", "power", positive=True), 1.0)


class TestParseNumberErrors(unittest.TestCase):
    def test_non_numeric(self):
        with self.assertRaises(ValueError):
            sh.parse_number("abc", "power")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            sh.parse_number("", "power")

    def test_inf(self):
        with self.assertRaises(ValueError):
            sh.parse_number("inf", "power")

    def test_neg_inf(self):
        with self.assertRaises(ValueError):
            sh.parse_number("-inf", "power")

    def test_nan(self):
        with self.assertRaises(ValueError):
            sh.parse_number("nan", "power")

    def test_positive_zero(self):
        with self.assertRaises(ValueError):
            sh.parse_number("0", "power", positive=True)

    def test_positive_negative(self):
        with self.assertRaises(ValueError):
            sh.parse_number("-1", "power", positive=True)


if __name__ == "__main__":
    unittest.main()