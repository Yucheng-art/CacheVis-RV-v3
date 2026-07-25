"""Tests for the reusable experiment runner."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from experiment_runner import run_single_experiment


class ExperimentRunnerTest(unittest.TestCase):
    """Covers single experiment summaries and exports."""

    def test_single_experiment_summary_fields(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        summary = run_single_experiment(
            "single test",
            config,
            "sequential",
            {"count": 4},
        )

        expected_fields = {
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
            "access_results",
        }
        self.assertTrue(expected_fields.issubset(summary.keys()))
        self.assertEqual(summary["total_accesses"], 4)
        self.assertEqual(len(summary["access_results"]), 4)

    def test_single_experiment_export_uses_temp_dir(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = run_single_experiment(
                "export test",
                config,
                "loop-reuse",
                {"count": 4},
                export=True,
                export_dir=temp_dir,
            )
            self.assertTrue(Path(summary["csv_path"]).exists())
            self.assertTrue(Path(summary["report_path"]).exists())


if __name__ == "__main__":
    unittest.main()
