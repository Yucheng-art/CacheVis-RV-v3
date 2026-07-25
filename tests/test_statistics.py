"""Tests for statistics helper functions."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from statistics import hit_rate, miss_rate, summarize_results


class StatisticsTest(unittest.TestCase):
    """Covers simple cache statistics summaries."""

    def test_rates_handle_empty_accesses(self):
        self.assertEqual(hit_rate(0, 0), 0.0)
        self.assertEqual(miss_rate(0, 0), 0.0)

    def test_summarize_results(self):
        summary = summarize_results(total_accesses=4, hits=3, misses=1)

        self.assertEqual(summary["total_accesses"], 4)
        self.assertEqual(summary["hits"], 3)
        self.assertEqual(summary["misses"], 1)
        self.assertEqual(summary["hit_rate"], 0.75)
        self.assertEqual(summary["miss_rate"], 0.25)


if __name__ == "__main__":
    unittest.main()
