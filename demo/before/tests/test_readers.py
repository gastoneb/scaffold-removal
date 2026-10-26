import json
import os
import tempfile
import unittest

from salesreport.readers import BaseReader, CsvReader, JsonReader, get_reader


class ReaderTestBase(unittest.TestCase):
    def write(self, name, content):
        directory = tempfile.mkdtemp()
        self.addCleanup(
            lambda: (
                [os.remove(os.path.join(directory, f)) for f in os.listdir(directory)]
                and os.rmdir(directory)
            )
        )
        path = os.path.join(directory, name)
        with open(path, "w") as handle:
            handle.write(content)
        return path


class CsvReaderTests(ReaderTestBase):
    def test_reads_rows(self):
        path = self.write("a.csv", "region,amount\nwest,1.5\neast,2\n")
        self.assertEqual(
            CsvReader().read(path),
            [{"region": "west", "amount": 1.5}, {"region": "east", "amount": 2.0}],
        )

    def test_strips_region_whitespace(self):
        path = self.write("a.csv", "region,amount\n west ,1\n")
        self.assertEqual(CsvReader().read(path)[0]["region"], "west")

    def test_empty_file_has_no_rows(self):
        path = self.write("a.csv", "region,amount\n")
        self.assertEqual(CsvReader().read(path), [])

    def test_missing_region_is_an_error(self):
        path = self.write("a.csv", "region,amount\n,1\n")
        with self.assertRaisesRegex(ValueError, "line 2: missing region"):
            CsvReader().read(path)

    def test_blank_region_is_an_error(self):
        path = self.write("a.csv", "region,amount\n   ,1\n")
        with self.assertRaises(ValueError):
            CsvReader().read(path)

    def test_invalid_amount_is_an_error(self):
        path = self.write("a.csv", "region,amount\nwest,abc\n")
        with self.assertRaisesRegex(ValueError, "line 2: invalid amount 'abc'"):
            CsvReader().read(path)

    def test_missing_amount_is_an_error(self):
        path = self.write("a.csv", "region,amount\nwest,\n")
        with self.assertRaises(ValueError):
            CsvReader().read(path)

    def test_error_reports_correct_line(self):
        path = self.write("a.csv", "region,amount\nwest,1\neast,x\n")
        with self.assertRaisesRegex(ValueError, "line 3"):
            CsvReader().read(path)

    def test_missing_file(self):
        with self.assertRaises(OSError):
            CsvReader().read("/no/such/file.csv")


class JsonReaderTests(ReaderTestBase):
    def test_reads_rows(self):
        path = self.write("a.json", json.dumps([{"region": "west", "amount": "3"}]))
        self.assertEqual(JsonReader().read(path), [{"region": "west", "amount": 3.0}])

    def test_missing_key(self):
        path = self.write("a.json", json.dumps([{"region": "west"}]))
        with self.assertRaises(KeyError):
            JsonReader().read(path)


class RegistryTests(unittest.TestCase):
    def test_csv(self):
        self.assertIsInstance(get_reader("csv"), CsvReader)

    def test_json(self):
        self.assertIsInstance(get_reader("json"), JsonReader)

    def test_unknown(self):
        with self.assertRaisesRegex(ValueError, "unknown input format: xml"):
            get_reader("xml")

    def test_base_reader_is_abstract(self):
        with self.assertRaises(TypeError):
            BaseReader()
