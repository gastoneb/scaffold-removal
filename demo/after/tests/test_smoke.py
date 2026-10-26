import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(csv_text):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sales.csv"
        path.write_text(csv_text)
        return subprocess.run(
            [sys.executable, "-m", "salesreport", str(path)],
            cwd=ROOT, capture_output=True, text=True,
        )


class SmokeTest(unittest.TestCase):
    def test_totals_per_region(self):
        result = run("region,amount\nwest,100.50\neast,40\nwest,20.25\neast,10.75\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"east": 50.75, "west": 120.75})

    def test_bad_row_is_rejected_with_its_line(self):
        result = run("region,amount\nwest,100\neast,oops\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("line 3: invalid amount 'oops'", result.stderr)
