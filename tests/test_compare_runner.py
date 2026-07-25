"""Tests for cache parameter comparison helpers."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from compare_runner import build_comparison_configs, compare_cache_configs, run_comparison


class CompareRunnerTest(unittest.TestCase):
    """Covers built-in ways, block-size, and cache-size comparisons."""

    def setUp(self):
        self.base_config = CacheConfig(
            cache_size_bytes=8 * 1024,
            block_size_bytes=32,
            ways=2,
        )

    def test_ways_comparison_returns_three_results(self):
        configs = build_comparison_configs("ways", self.base_config)
        summaries = run_comparison("ways", "conflict", {"count": 16}, configs)
        self.assertEqual(len(summaries), 3)
        self.assertEqual([summary["ways"] for summary in summaries], [1, 2, 4])

    def test_block_size_comparison_returns_three_results(self):
        configs = build_comparison_configs("block-size", self.base_config)
        summaries = run_comparison("block", "stride", {"count": 16}, configs)
        self.assertEqual(len(summaries), 3)
        self.assertEqual(
            [summary["block_size_bytes"] for summary in summaries],
            [16, 32, 64],
        )

    def test_cache_size_comparison_exports_report(self):
        configs = build_comparison_configs("cache-size", self.base_config)
        with tempfile.TemporaryDirectory() as temp_dir:
            summaries = run_comparison(
                "cache size comparison",
                "sequential",
                {"count": 16},
                configs,
                export=True,
                export_dir=temp_dir,
            )
            report_path = Path(summaries[0]["comparison_report_path"])
            self.assertTrue(report_path.exists())

        self.assertEqual(len(summaries), 3)
        self.assertEqual(
            [summary["cache_size_bytes"] for summary in summaries],
            [4096, 8192, 16384],
        )

    def test_summary_fields_are_complete(self):
        configs = build_comparison_configs("ways", self.base_config)
        summaries = compare_cache_configs("loop-reuse", {"count": 8}, configs)

        expected_fields = {
            "config_name",
            "experiment_name",
            "trace_type",
            "trace_params",
            "cache_size_bytes",
            "block_size_bytes",
            "ways",
            "replacement_policy",
            "write_policy",
            "sets",
            "total_accesses",
            "hits",
            "misses",
            "hit_rate",
            "miss_rate",
        }
        self.assertTrue(expected_fields.issubset(summaries[0].keys()))

    def test_unknown_comparison_mode_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "ways, block-size, cache-size"):
            build_comparison_configs("latency", self.base_config)


if __name__ == "__main__":
    unittest.main()
