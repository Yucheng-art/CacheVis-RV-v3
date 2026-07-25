"""Tests for CSV and Markdown report exports."""

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from report_exporter import (
    ACCESS_LOG_FIELDS,
    build_comparison_conclusion,
    export_access_log_csv,
    export_comparison_markdown_report,
    export_markdown_report,
)


class ReportExporterTest(unittest.TestCase):
    """Covers writing experiment outputs to temporary files."""

    def test_export_access_log_csv(self):
        access_log = [
            {
                "access_id": 1,
                "address": 4096,
                "operation": "read",
                "tag": 8,
                "index": 0,
                "offset": 0,
                "hit": False,
                "victim_way": 0,
                "replaced_valid": False,
                "replaced_tag": None,
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "access_log.csv"
            export_access_log_csv(access_log, output_path)

            with output_path.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                self.assertEqual(reader.fieldnames, ACCESS_LOG_FIELDS)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["access_id"], "1")
        self.assertEqual(rows[0]["address"], "4096")
        self.assertEqual(rows[0]["hit"], "False")

    def test_export_markdown_report(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        summary = {
            "total_accesses": 2,
            "hits": 1,
            "misses": 1,
            "hit_rate": 0.5,
            "miss_rate": 0.5,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.md"
            export_markdown_report(
                output_path,
                software_name="CacheVis-RV",
                software_version="V0.3",
                experiment_name="Unit Test Experiment",
                cache_config=config,
                trace_type="sequential",
                summary=summary,
                conclusion="Report export works.",
            )
            content = output_path.read_text(encoding="utf-8")

        self.assertIn("# Unit Test Experiment", content)
        self.assertIn("- Software: CacheVis-RV", content)
        self.assertIn("- Hit rate: 50.00%", content)
        self.assertIn("Report export works.", content)

    def test_export_comparison_markdown_report(self):
        summaries = [
            {
                "config_name": "1-way",
                "cache_size_bytes": 8192,
                "block_size_bytes": 32,
                "ways": 1,
                "replacement_policy": "LRU",
                "total_accesses": 4,
                "hits": 2,
                "misses": 2,
                "hit_rate": 0.5,
                "miss_rate": 0.5,
            },
            {
                "config_name": "2-way",
                "cache_size_bytes": 8192,
                "block_size_bytes": 32,
                "ways": 2,
                "replacement_policy": "LRU",
                "total_accesses": 4,
                "hits": 3,
                "misses": 1,
                "hit_rate": 0.75,
                "miss_rate": 0.25,
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "comparison.md"
            export_comparison_markdown_report(
                output_path,
                software_name="CacheVis-RV",
                software_version="V0.3",
                comparison_name="Ways Comparison",
                trace_type="conflict",
                trace_params={"count": 4},
                summaries=summaries,
            )
            content = output_path.read_text(encoding="utf-8")

        self.assertIn("# Ways Comparison", content)
        self.assertIn("| Config | Cache size | Block size | Ways |", content)
        self.assertIn("2-way", content)
        self.assertIn("Highest hit rate: 2-way", content)

    def test_comparison_conclusion_reports_ties(self):
        summaries = [
            {
                "config_name": "A",
                "hit_rate": 0.75,
                "misses": 2,
            },
            {
                "config_name": "B",
                "hit_rate": 0.75,
                "misses": 2,
            },
            {
                "config_name": "C",
                "hit_rate": 0.5,
                "misses": 4,
            },
        ]

        conclusion = build_comparison_conclusion(summaries)

        self.assertIn("Tie for highest hit rate: A, B", conclusion)
        self.assertIn("Tie for fewest misses: A, B", conclusion)


if __name__ == "__main__":
    unittest.main()
