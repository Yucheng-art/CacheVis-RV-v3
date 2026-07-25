"""Compatibility tests for packaged experiment and reporting services."""

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from cachevis_rv.experiments import (
    generate_conflict_trace,
    generate_matrix_column_like_trace,
    generate_matrix_row_major_trace,
    generate_random_trace,
    generate_sequential_trace,
    generate_stride_trace,
)
from cachevis_rv.labs.compare_experiment import (
    build_comparison_configs,
    compare_cache_configs,
    run_comparison,
)
from cachevis_rv.labs.single_experiment import (
    DEFAULT_START_ADDRESS,
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    build_trace,
    make_single_experiment_conclusion,
    run_single_experiment,
)
from cachevis_rv.services import (
    ACCESS_LOG_FIELDS,
    COMPARISON_FIELDS,
    build_comparison_conclusion,
    export_access_log_csv,
    export_comparison_markdown_report,
    export_markdown_report,
)
from compare_runner import (
    build_comparison_configs as flat_build_comparison_configs,
    compare_cache_configs as flat_compare_cache_configs,
    run_comparison as flat_run_comparison,
)
from experiment_runner import (
    DEFAULT_START_ADDRESS as FLAT_DEFAULT_START_ADDRESS,
    SOFTWARE_NAME as FLAT_SOFTWARE_NAME,
    SOFTWARE_VERSION as FLAT_SOFTWARE_VERSION,
    build_trace as flat_build_trace,
    make_single_experiment_conclusion as flat_make_single_experiment_conclusion,
    run_single_experiment as flat_run_single_experiment,
)
from report_exporter import (
    ACCESS_LOG_FIELDS as FLAT_ACCESS_LOG_FIELDS,
    COMPARISON_FIELDS as FLAT_COMPARISON_FIELDS,
    build_comparison_conclusion as flat_build_comparison_conclusion,
    export_access_log_csv as flat_export_access_log_csv,
    export_comparison_markdown_report as flat_export_comparison_markdown_report,
    export_markdown_report as flat_export_markdown_report,
)
from trace_generator import (
    generate_conflict_trace as flat_generate_conflict_trace,
    generate_matrix_column_like_trace as flat_generate_matrix_column_like_trace,
    generate_matrix_row_major_trace as flat_generate_matrix_row_major_trace,
    generate_random_trace as flat_generate_random_trace,
    generate_sequential_trace as flat_generate_sequential_trace,
    generate_stride_trace as flat_generate_stride_trace,
)


class ExperimentServicesPackageCompatibilityTest(unittest.TestCase):
    """Proves packaged services preserve the stable flat-module behavior."""

    def test_trace_facade_exports_same_implementation_objects(self):
        self.assertIs(flat_generate_sequential_trace, generate_sequential_trace)
        self.assertIs(flat_generate_stride_trace, generate_stride_trace)
        self.assertIs(flat_generate_random_trace, generate_random_trace)
        self.assertIs(flat_generate_conflict_trace, generate_conflict_trace)
        self.assertIs(flat_generate_matrix_row_major_trace, generate_matrix_row_major_trace)
        self.assertIs(
            flat_generate_matrix_column_like_trace,
            generate_matrix_column_like_trace,
        )

    def test_runner_facades_export_same_implementation_objects(self):
        self.assertIs(flat_build_trace, build_trace)
        self.assertIs(flat_run_single_experiment, run_single_experiment)
        self.assertIs(
            flat_make_single_experiment_conclusion,
            make_single_experiment_conclusion,
        )
        self.assertEqual(FLAT_SOFTWARE_NAME, SOFTWARE_NAME)
        self.assertEqual(FLAT_SOFTWARE_VERSION, SOFTWARE_VERSION)
        self.assertEqual(FLAT_DEFAULT_START_ADDRESS, DEFAULT_START_ADDRESS)
        self.assertIs(flat_compare_cache_configs, compare_cache_configs)
        self.assertIs(flat_build_comparison_configs, build_comparison_configs)
        self.assertIs(flat_run_comparison, run_comparison)

    def test_report_facade_exports_same_objects_and_fields(self):
        self.assertIs(FLAT_ACCESS_LOG_FIELDS, ACCESS_LOG_FIELDS)
        self.assertIs(FLAT_COMPARISON_FIELDS, COMPARISON_FIELDS)
        self.assertIs(flat_export_access_log_csv, export_access_log_csv)
        self.assertIs(flat_export_markdown_report, export_markdown_report)
        self.assertIs(
            flat_export_comparison_markdown_report,
            export_comparison_markdown_report,
        )
        self.assertIs(flat_build_comparison_conclusion, build_comparison_conclusion)

    def test_key_trace_algorithms_are_unchanged(self):
        self.assertEqual(
            generate_sequential_trace(0x1000, 4, step=4),
            [0x1000, 0x1004, 0x1008, 0x100C],
        )
        self.assertEqual(
            generate_stride_trace(0x2000, 4, stride_bytes=16),
            [0x2000, 0x2010, 0x2020, 0x2030],
        )
        random_trace = generate_random_trace(
            0x1000,
            6,
            address_range_bytes=64,
            alignment=4,
            seed=7,
        )
        self.assertEqual(
            random_trace,
            flat_generate_random_trace(
                0x1000,
                6,
                address_range_bytes=64,
                alignment=4,
                seed=7,
            ),
        )
        self.assertTrue(all((address - 0x1000) % 4 == 0 for address in random_trace))
        self.assertEqual(
            generate_conflict_trace(0x1000, 5, conflict_stride_bytes=0x1000),
            [0x1000, 0x2000, 0x3000, 0x4000, 0x1000],
        )
        self.assertEqual(
            generate_matrix_row_major_trace(0x1000, 2),
            [0x1000, 0x1004, 0x1008, 0x100C],
        )
        self.assertEqual(
            generate_matrix_column_like_trace(0x1000, 2),
            [0x1000, 0x1008, 0x1004, 0x100C],
        )

    def test_single_experiment_fixed_result_is_unchanged(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)

        summary = run_single_experiment(
            "package compatibility",
            config,
            "sequential",
            {"count": 4},
        )

        self.assertEqual(summary["total_accesses"], 4)
        self.assertEqual(summary["hits"], 3)
        self.assertEqual(summary["misses"], 1)
        self.assertEqual(summary["hit_rate"], 0.75)
        self.assertEqual(summary["miss_rate"], 0.25)
        self.assertEqual(len(summary["access_results"]), 4)

    def test_all_comparison_modes_are_unchanged(self):
        base = CacheConfig(cache_size_bytes=8192, block_size_bytes=32, ways=2)
        expected = {
            "ways": ("ways", [1, 2, 4]),
            "block-size": ("block_size_bytes", [16, 32, 64]),
            "cache-size": ("cache_size_bytes", [4096, 8192, 16384]),
        }

        for mode, (field, values) in expected.items():
            with self.subTest(mode=mode):
                configs = build_comparison_configs(mode, base)
                summaries = compare_cache_configs("sequential", {"count": 8}, configs)
                self.assertEqual([summary[field] for summary in summaries], values)
                self.assertEqual(len(summaries), 3)

    def test_csv_export_header_and_key_fields_are_unchanged(self):
        access_results = [
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
            path = export_access_log_csv(
                access_results,
                Path(temp_dir) / "access_log.csv",
            )
            with path.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                fieldnames = reader.fieldnames

        self.assertEqual(fieldnames, ACCESS_LOG_FIELDS)
        self.assertEqual(rows[0]["access_id"], "1")
        self.assertEqual(rows[0]["address"], "4096")
        self.assertEqual(rows[0]["hit"], "False")

    def test_single_markdown_report_content_is_unchanged(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        summary = {
            "total_accesses": 4,
            "hits": 3,
            "misses": 1,
            "hit_rate": 0.75,
            "miss_rate": 0.25,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = export_markdown_report(
                Path(temp_dir) / "single.md",
                software_name="CacheVis-RV",
                software_version="V1.0",
                experiment_name="Single Compatibility",
                cache_config=config,
                trace_type="sequential",
                summary=summary,
                conclusion="Stable behavior.",
            )
            content = path.read_text(encoding="utf-8")

        self.assertIn("# Single Compatibility", content)
        self.assertIn("## Cache Configuration", content)
        self.assertIn("## Statistics", content)
        self.assertIn("- Hits: 3", content)
        self.assertIn("- Hit rate: 75.00%", content)

    def test_comparison_markdown_report_content_is_unchanged(self):
        base = CacheConfig(cache_size_bytes=8192, block_size_bytes=32, ways=2)
        summaries = compare_cache_configs(
            "sequential",
            {"count": 8},
            build_comparison_configs("ways", base),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = export_comparison_markdown_report(
                Path(temp_dir) / "compare.md",
                software_name="CacheVis-RV",
                software_version="V1.0",
                comparison_name="Ways Compatibility",
                trace_type="sequential",
                trace_params={"count": 8},
                summaries=summaries,
            )
            content = path.read_text(encoding="utf-8")

        self.assertIn("# Ways Compatibility", content)
        self.assertIn("## Comparison Table", content)
        self.assertIn("| Config | Cache size | Block size | Ways |", content)
        self.assertIn("1-way", content)
        self.assertIn("2-way", content)
        self.assertIn("4-way", content)
        self.assertIn("## Conclusion", content)


if __name__ == "__main__":
    unittest.main()
