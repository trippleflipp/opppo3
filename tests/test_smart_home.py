import io
import unittest
from contextlib import redirect_stdout

import main as sh


class _PopulatedHome(unittest.TestCase):
    """База: контейнер с набором устройств для тестов REM."""
    def setUp(self):
        self.home = sh.SmartHome()
        self.home._add(["LAMP", "Xiaomi", "10", "E27"])
        self.home._add(["LAMP", "Philips", "15", "E14"])
        self.home._add(["THERMOSTAT", "Aqara", "16", "28"])
        self.home._add(["SOCKET", "TP-Link", "3500"])


class TestAdd(unittest.TestCase):
    def setUp(self):
        self.home = sh.SmartHome()

    def test_add_lamp(self):
        self.home._add(["LAMP", "Xiaomi", "10", "E27"])
        self.assertIsInstance(self.home.devices[0], sh.SmartLamp)

    def test_add_thermostat(self):
        self.home._add(["THERMOSTAT", "Aqara", "16", "28"])
        self.assertIsInstance(self.home.devices[0], sh.Thermostat)

    def test_add_socket(self):
        self.home._add(["SOCKET", "TP-Link", "3500"])
        self.assertIsInstance(self.home.devices[0], sh.SmartSocket)

    def test_type_case_insensitive(self):
        self.home._add(["lamp", "Xiaomi", "10", "E27"])
        self.assertEqual(len(self.home.devices), 1)

    def test_empty_arguments(self):
        with self.assertRaises(ValueError):
            self.home._add([])

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            self.home._add(["UNKNOWN"])

    def test_too_few_params(self):
        with self.assertRaises(ValueError):
            self.home._add(["LAMP", "Xiaomi", "10"])

    def test_too_many_params(self):
        with self.assertRaises(ValueError):
            self.home._add(["LAMP", "Xiaomi", "10", "E27", "extra"])

    def test_invalid_power_propagates(self):
        with self.assertRaises(ValueError):
            self.home._add(["LAMP", "Xiaomi", "abc", "E27"])


class TestRemove(_PopulatedHome):
    def _lamps(self):
        return [d for d in self.home.devices if isinstance(d, sh.SmartLamp)]

    def test_eq(self):
        self.home._remove(["power", "==", "10"])
        self.assertNotIn(10.0, [l.power for l in self._lamps()])

    def test_ne(self):
        self.home._remove(["power", "!=", "10"])
        self.assertEqual([l.power for l in self._lamps()], [10.0])

    def test_gt(self):
        self.home._remove(["power", ">", "10"])
        self.assertEqual([l.power for l in self._lamps()], [10.0])

    def test_lt(self):
        self.home._remove(["power", "<", "15"])
        self.assertEqual([l.power for l in self._lamps()], [15.0])

    def test_ge(self):
        self.home._remove(["power", ">=", "10"])
        self.assertEqual(self._lamps(), [])

    def test_le(self):
        self.home._remove(["power", "<=", "10"])
        self.assertEqual([l.power for l in self._lamps()], [15.0])

    def test_type_eq(self):
        self.home._remove(["type", "==", "lamp"])
        self.assertEqual(len(self.home.devices), 2)

    def test_type_eq_uppercase_arg(self):
        self.home._remove(["type", "==", "LAMP"])
        self.assertEqual(len(self.home.devices), 2)

    def test_type_ne(self):
        self.home._remove(["type", "!=", "LAMP"])
        self.assertTrue(all(isinstance(d, sh.SmartLamp) for d in self.home.devices))

    def test_manufacturer_eq(self):
        self.home._remove(["manufacturer", "==", "Xiaomi"])
        self.assertFalse(any(d.manufacturer == "Xiaomi" for d in self.home.devices))

    def test_base_eq(self):
        self.home._remove(["base", "==", "E14"])
        self.assertNotIn("E14", [l.base for l in self._lamps()])

    def test_other_devices_survive_remove_by_power(self):
        self.home._remove(["power", "==", "10"])
        types = {type(d) for d in self.home.devices}
        self.assertIn(sh.Thermostat, types)
        self.assertIn(sh.SmartSocket, types)

    def test_no_matches_keeps_all(self):
        before = len(self.home.devices)
        self.home._remove(["power", ">", "10000"])
        self.assertEqual(len(self.home.devices), before)

    def test_wrong_arg_count(self):
        with self.assertRaises(ValueError):
            self.home._remove(["power", "=="])

    def test_unknown_field(self):
        with self.assertRaises(ValueError):
            self.home._remove(["foo", "==", "1"])

    def test_unknown_operator(self):
        with self.assertRaises(ValueError):
            self.home._remove(["power", "<>", "1"])

    def test_numeric_operator_on_text_field(self):
        with self.assertRaises(ValueError):
            self.home._remove(["manufacturer", ">", "Xiaomi"])


class TestExecute(unittest.TestCase):
    def setUp(self):
        self.home = sh.SmartHome()

    def test_add_with_quotes(self):
        self.home.execute('ADD LAMP "Some Manufacturer" 10 E27')
        self.assertEqual(self.home.devices[0].manufacturer, "Some Manufacturer")

    def test_add_case_insensitive(self):
        self.home.execute('add lamp "Xiaomi" 10 E27')
        self.assertEqual(len(self.home.devices), 1)

    def test_rem(self):
        self.home.execute('ADD LAMP "Xiaomi" 10 E27')
        self.home.execute("REM manufacturer == Xiaomi")
        self.assertEqual(self.home.devices, [])

    def test_print_empty(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.home.execute("PRINT")
        self.assertIn("Контейнер пуст", buf.getvalue())

    def test_print_with_args_raises(self):
        with self.assertRaises(ValueError):
            self.home.execute("PRINT extra")

    def test_unknown_command(self):
        with self.assertRaises(ValueError):
            self.home.execute("FOO")

    def test_empty_line_ignored(self):
        self.home.execute("")
        self.home.execute("   ")
        self.assertEqual(self.home.devices, [])

    def test_comment_ignored(self):
        self.home.execute("# this is a comment")
        self.assertEqual(self.home.devices, [])


class TestPrintDevices(unittest.TestCase):
    def test_empty(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            sh.SmartHome().print_devices()
        out = buf.getvalue()
        self.assertIn("0", out)
        self.assertIn("Контейнер пуст", out)

    def test_non_empty(self):
        home = sh.SmartHome()
        home._add(["LAMP", "Xiaomi", "10", "E27"])
        home._add(["SOCKET", "TP-Link", "3500"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            home.print_devices()
        out = buf.getvalue()
        for token in ("2", "1.", "2.", "Xiaomi", "TP-Link"):
            self.assertIn(token, out)


if __name__ == "__main__":
    unittest.main()