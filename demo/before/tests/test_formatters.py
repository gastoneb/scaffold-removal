import unittest
from collections import OrderedDict

from salesreport.formatters import (
    BaseFormatter,
    JsonFormatter,
    TextFormatter,
    XmlFormatter,
    get_formatter,
)

TOTALS = OrderedDict([("east", 50.75), ("west", 120.75)])


class JsonFormatterTests(unittest.TestCase):
    def test_output(self):
        self.assertEqual(
            JsonFormatter().format(TOTALS),
            '{\n  "east": 50.75,\n  "west": 120.75\n}',
        )

    def test_empty(self):
        self.assertEqual(JsonFormatter().format(OrderedDict()), "{}")


class TextFormatterTests(unittest.TestCase):
    def test_output(self):
        self.assertEqual(TextFormatter().format(TOTALS), "east: 50.75\nwest: 120.75")

    def test_empty(self):
        self.assertEqual(TextFormatter().format(OrderedDict()), "")


class XmlFormatterTests(unittest.TestCase):
    def test_output(self):
        self.assertEqual(
            XmlFormatter().format(TOTALS),
            '<totals>\n  <region name="east">50.75</region>\n'
            '  <region name="west">120.75</region>\n</totals>',
        )

    def test_escapes_names(self):
        output = XmlFormatter().format(OrderedDict([("a&b", 1.0)]))
        self.assertIn("a&amp;b", output)


class RegistryTests(unittest.TestCase):
    def test_known_formats(self):
        self.assertIsInstance(get_formatter("json"), JsonFormatter)
        self.assertIsInstance(get_formatter("text"), TextFormatter)
        self.assertIsInstance(get_formatter("xml"), XmlFormatter)

    def test_unknown(self):
        with self.assertRaisesRegex(ValueError, "unknown output format: yaml"):
            get_formatter("yaml")

    def test_base_is_abstract(self):
        with self.assertRaises(TypeError):
            BaseFormatter()
