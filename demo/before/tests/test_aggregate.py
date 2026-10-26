import unittest
from collections import OrderedDict

from salesreport.aggregate import aggregate

ROWS = [
    {"region": "west", "amount": 100.5},
    {"region": "east", "amount": 40.0},
    {"region": "west", "amount": 20.25},
]


class AggregateTests(unittest.TestCase):
    def test_sums_by_region(self):
        self.assertEqual(aggregate(ROWS), {"east": 40.0, "west": 120.75})

    def test_returns_ordered_dict(self):
        self.assertIsInstance(aggregate(ROWS), OrderedDict)

    def test_sorted_by_region_by_default(self):
        self.assertEqual(list(aggregate(ROWS)), ["east", "west"])

    def test_sort_by_total(self):
        self.assertEqual(list(aggregate(ROWS, sort_by="total")), ["west", "east"])

    def test_unknown_sort_key(self):
        with self.assertRaisesRegex(ValueError, "unknown sort key: size"):
            aggregate(ROWS, sort_by="size")

    def test_rounding(self):
        rows = [{"region": "a", "amount": 0.1}, {"region": "a", "amount": 0.2}]
        self.assertEqual(aggregate(rows), {"a": 0.3})

    def test_custom_decimals(self):
        rows = [{"region": "a", "amount": 1.2345}]
        self.assertEqual(aggregate(rows, decimals=1), {"a": 1.2})

    def test_empty(self):
        self.assertEqual(aggregate([]), {})

    def test_single_row(self):
        self.assertEqual(aggregate(ROWS[:1]), {"west": 100.5})
