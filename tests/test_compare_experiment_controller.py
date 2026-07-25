"""Tests for the pure Compare Experiment lab controller."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.compare_experiment.controller import (
    CompareExperimentController,
)


class CompareExperimentControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = CompareExperimentController()
        self.base_config = CacheConfig(
            cache_size_bytes=8192,
            block_size_bytes=32,
            ways=2,
            replacement_policy="LRU",
        )

    def test_controller_and_view_model_do_not_depend_on_pyside6(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "compare_experiment"
        )
        for name in ("controller.py", "view_model.py"):
            with self.subTest(name=name):
                self.assertNotIn(
                    "PySide6",
                    (package / name).read_text(encoding="utf-8"),
                )

    def test_initial_state_is_empty_and_not_exportable(self):
        state = self.controller.state

        self.assertIsNone(state.comparison_type)
        self.assertIsNone(state.comparison_name)
        self.assertEqual(state.rows, ())
        self.assertFalse(state.has_exportable_result)

    def test_ways_comparison_matches_existing_behavior(self):
        state = self.controller.run(
            "ways GUI comparison on conflict trace",
            "ways",
            "conflict",
            {"count": 8},
            self.base_config,
        )

        self.assertEqual([row["config_name"] for row in state.rows], [
            "1-way",
            "2-way",
            "4-way",
        ])
        self.assertEqual([row["hits"] for row in state.rows], [0, 0, 4])

    def test_block_size_comparison_matches_existing_behavior(self):
        state = self.controller.run(
            "block-size GUI comparison on sequential trace",
            "block-size",
            "sequential",
            {"count": 8},
            self.base_config,
        )

        self.assertEqual([row["config_name"] for row in state.rows], [
            "16B block",
            "32B block",
            "64B block",
        ])
        self.assertEqual([row["hits"] for row in state.rows], [6, 7, 7])

    def test_cache_size_comparison_matches_existing_behavior(self):
        state = self.controller.run(
            "cache-size GUI comparison on conflict trace",
            "cache-size",
            "conflict",
            {"count": 8},
            self.base_config,
        )

        self.assertEqual([row["config_name"] for row in state.rows], [
            "4KB cache",
            "8KB cache",
            "16KB cache",
        ])
        self.assertEqual([row["cache_size_bytes"] for row in state.rows], [
            4096,
            8192,
            16384,
        ])
        self.assertTrue(state.conclusion)
        self.assertTrue(state.has_exportable_result)

    def test_clear_restores_initial_state(self):
        self.controller.run(
            "ways GUI comparison on conflict trace",
            "ways",
            "conflict",
            {"count": 8},
            self.base_config,
        )

        state = self.controller.clear()

        self.assertEqual(state.rows, ())
        self.assertEqual(state.conclusion, "")
        self.assertFalse(state.has_exportable_result)

    def test_markdown_export_preserves_fields_and_titles(self):
        self.controller.run(
            "ways GUI comparison on conflict trace",
            "ways",
            "conflict",
            {"count": 8},
            self.base_config,
        )

        with tempfile.TemporaryDirectory() as directory:
            report_path = self.controller.export(directory)
            report_text = report_path.read_text(encoding="utf-8")

        self.assertEqual(
            report_path.name,
            "ways_gui_comparison_on_conflict_trace.md",
        )
        self.assertIn("# ways GUI comparison on conflict trace", report_text)
        self.assertIn("## Comparison Table", report_text)
        self.assertIn("| Config | Cache size | Block size | Ways |", report_text)
        self.assertIn("## Conclusion", report_text)


if __name__ == "__main__":
    unittest.main()
