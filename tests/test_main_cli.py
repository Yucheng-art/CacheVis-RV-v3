"""Tests for reusable main module helpers."""

import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from main import (
    build_comparison_configs,
    build_arg_parser,
    build_trace,
    export_results,
    run_comparison,
    run_experiment,
)


class MainCliHelperTest(unittest.TestCase):
    """Covers main helpers without invoking a shell command."""

    def test_build_trace_sequential(self):
        self.assertEqual(build_trace("sequential", 3), [0x1000, 0x1004, 0x1008])

    def test_build_trace_conflict(self):
        self.assertEqual(
            build_trace("conflict", 5),
            [0x1000, 0x2000, 0x3000, 0x4000, 0x1000],
        )

    def test_run_experiment_and_export_results(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        access_log, summary = run_experiment(config, [0x00, 0x04])

        self.assertEqual(len(access_log), 2)
        self.assertEqual(summary["hits"], 1)
        self.assertEqual(summary["misses"], 1)

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path, report_path = export_results(
                Path(temp_dir), "sequential", config, access_log, summary
            )
            self.assertTrue(csv_path.exists())
            self.assertTrue(report_path.exists())

    def test_compare_mode_helpers(self):
        config = CacheConfig(cache_size_bytes=8192, block_size_bytes=32, ways=2)
        configs = build_comparison_configs("ways", config)
        summaries = run_comparison(
            "ways comparison",
            "sequential",
            {"count": 8},
            configs,
            export=False,
        )

        self.assertEqual(len(summaries), 3)
        self.assertEqual([summary["ways"] for summary in summaries], [1, 2, 4])

    def test_negative_count_is_argparse_error(self):
        parser = build_arg_parser()
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["--count", "-1"])

    def test_invalid_compare_is_argparse_error(self):
        parser = build_arg_parser()
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["--compare", "latency"])

    def test_gui_flag_parses_without_affecting_cli_defaults(self):
        parser = build_arg_parser()
        args = parser.parse_args(["--gui"])

        self.assertTrue(args.gui)
        self.assertEqual(args.trace, "sequential")
        self.assertEqual(args.count, 32)


if __name__ == "__main__":
    unittest.main()
