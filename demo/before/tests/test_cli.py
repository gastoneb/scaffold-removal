import io
import os
import tempfile
import unittest

from salesreport.cli import main

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "sample.csv")


def run(argv, env=None):
    out, err = io.StringIO(), io.StringIO()
    code = main(argv, env or {}, out, err)
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def test_default_json(self):
        code, out, err = run([SAMPLE])
        self.assertEqual(code, 0)
        self.assertEqual(
            out, '{\n  "east": 50.75,\n  "north": 5.0,\n  "west": 120.75\n}\n'
        )
        self.assertEqual(err, "")

    def test_text_output(self):
        code, out, _ = run([SAMPLE], {"SALESREPORT_OUTPUT": "text"})
        self.assertEqual(code, 0)
        self.assertEqual(out, "east: 50.75\nnorth: 5.0\nwest: 120.75\n")

    def test_xml_output(self):
        code, out, _ = run([SAMPLE], {"SALESREPORT_OUTPUT": "xml"})
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("<totals>"))

    def test_sort_by_total(self):
        _, out, _ = run(
            [SAMPLE], {"SALESREPORT_SORT": "total", "SALESREPORT_OUTPUT": "text"}
        )
        self.assertEqual(out.splitlines()[0], "west: 120.75")

    def test_verbose_logs_to_stderr(self):
        _, _, err = run([SAMPLE], {"SALESREPORT_VERBOSE": "1"})
        self.assertIn("[INFO] reading", err)
        self.assertIn("[DEBUG] read 5 rows", err)

    def test_debug_dump(self):
        _, _, err = run(
            [SAMPLE], {"SALESREPORT_VERBOSE": "1", "SALESREPORT_DEBUG": "1"}
        )
        self.assertIn("rows:", err)

    def test_usage(self):
        code, _, err = run([])
        self.assertEqual(code, 2)
        self.assertIn("usage", err)

    def test_too_many_args(self):
        self.assertEqual(run(["a", "b"])[0], 2)

    def test_missing_file(self):
        code, _, err = run(["/no/such/file.csv"])
        self.assertEqual(code, 1)
        self.assertIn("error:", err)

    def test_bad_row(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as handle:
            handle.write("region,amount\nwest,oops\n")
        self.addCleanup(os.remove, handle.name)
        code, out, err = run([handle.name])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("line 2: invalid amount 'oops'", err)

    def test_unknown_output_format(self):
        code, _, err = run([SAMPLE], {"SALESREPORT_OUTPUT": "yaml"})
        self.assertEqual(code, 1)
        self.assertIn("unknown output format", err)
