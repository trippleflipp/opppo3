import unittest

import main as sh


class TestSmartDeviceAbstract(unittest.TestCase):
    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            sh.SmartDevice("Xiaomi")


class TestSmartLamp(unittest.TestCase):
    def test_create_ok(self):
        lamp = sh.SmartLamp("Xiaomi", "10", "E27")
        self.assertEqual(lamp.manufacturer, "Xiaomi")
        self.assertEqual(lamp.power, 10.0)
        self.assertEqual(lamp.base, "E27")
        self.assertEqual(lamp.device_type, "LAMP")

    def test_manufacturer_stripped(self):
        self.assertEqual(sh.SmartLamp("  Xiaomi  ", "10", "E27").manufacturer, "Xiaomi")

    def test_empty_manufacturer(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("", "10", "E27")

    def test_whitespace_manufacturer(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("   ", "10", "E27")

    def test_power_zero(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("Xiaomi", "0", "E27")

    def test_power_negative(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("Xiaomi", "-3", "E27")

    def test_power_nan(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("Xiaomi", "abc", "E27")

    def test_empty_base(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("Xiaomi", "10", "")

    def test_whitespace_base(self):
        with self.assertRaises(ValueError):
            sh.SmartLamp("Xiaomi", "10", "   ")

    def test_str(self):
        s = str(sh.SmartLamp("Xiaomi", "10", "E27"))
        for token in ("Умная лампочка", "Xiaomi", "10", "E27"):
            self.assertIn(token, s)


class TestThermostat(unittest.TestCase):
    def test_create_ok(self):
        t = sh.Thermostat("Aqara", "16", "28")
        self.assertEqual((t.min_temp, t.max_temp), (16.0, 28.0))
        self.assertEqual(t.device_type, "THERMOSTAT")

    def test_negative_range(self):
        t = sh.Thermostat("Aqara", "-10", "10")
        self.assertEqual(t.min_temp, -10.0)

    def test_equal_bounds(self):
        self.assertEqual(sh.Thermostat("Aqara", "20", "20").min_temp, 20.0)

    def test_min_greater_max(self):
        with self.assertRaises(ValueError):
            sh.Thermostat("Aqara", "30", "20")

    def test_min_non_numeric(self):
        with self.assertRaises(ValueError):
            sh.Thermostat("Aqara", "abc", "20")

    def test_max_non_numeric(self):
        with self.assertRaises(ValueError):
            sh.Thermostat("Aqara", "20", "abc")

    def test_str(self):
        s = str(sh.Thermostat("Aqara", "16", "28"))
        for token in ("Термостат", "Aqara", "16", "28"):
            self.assertIn(token, s)


class TestSmartSocket(unittest.TestCase):
    def test_create_ok(self):
        s = sh.SmartSocket("TP-Link", "3500")
        self.assertEqual(s.max_load, 3500.0)
        self.assertEqual(s.device_type, "SOCKET")

    def test_zero_load(self):
        with self.assertRaises(ValueError):
            sh.SmartSocket("TP-Link", "0")

    def test_negative_load(self):
        with self.assertRaises(ValueError):
            sh.SmartSocket("TP-Link", "-100")

    def test_non_numeric_load(self):
        with self.assertRaises(ValueError):
            sh.SmartSocket("TP-Link", "abc")

    def test_str(self):
        s = str(sh.SmartSocket("TP-Link", "3500"))
        self.assertIn("TP-Link", s)
        self.assertIn("3500", s)


if __name__ == "__main__":
    unittest.main()