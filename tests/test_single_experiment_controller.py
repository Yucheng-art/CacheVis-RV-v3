"""Tests for the pure Single Experiment lab controller."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.single_experiment.controller import (
    SingleExperimentController,
)


class SingleExperimentControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = SingleExperimentController()
        self.config = CacheConfig(
            cache_size_bytes=64,
            block_size_bytes=16,
            ways=1,
            replacement_policy="LRU",
        )

    def test_controller_and_view_model_do_not_depend_on_pyside6(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "single_experiment"
        )
        for name in ("controller.py", "view_model.py"):
            with self.subTest(name=name):
                self.assertNotIn(
                    "PySide6",
                    (package / name).read_text(encoding="utf-8"),
                )

    def test_initial_state_is_empty_and_not_exportable(self):
        state = self.controller.state

        self.assertIsNone(state.cache_config)
        self.assertIsNone(state.summary)
        self.assertEqual(state.access_log, ())
        self.assertEqual(state.conclusion, "")
        self.assertFalse(state.has_exportable_result)

    def test_sequential_fixed_configuration_matches_existing_behavior(self):
        state = self.controller.run(
            "Sequential GUI Experiment",
            self.config,
            "sequential",
            {"count": 8},
        )

        self.assertEqual(state.summary["total_accesses"], 8)
        self.assertEqual(state.summary["hits"], 6)
        self.assertEqual(state.summary["misses"], 2)
        self.assertEqual(state.summary["hit_rate"], 0.75)
        self.assertEqual(state.summary["miss_rate"], 0.25)
        self.assertEqual(len(state.access_log), 8)
        self.assertTrue(state.has_exportable_result)

    def test_summary_access_log_and_conclusion_are_retained(self):
        state = self.controller.run(
            "Sequential GUI Experiment",
            self.config,
            "sequential",
            {"count": 8},
        )

        self.assertIs(state.cache_config, self.config)
        self.assertEqual(
            [row["hit"] for row in state.access_log],
            [False, True, True, True, False, True, True, True],
        )
        self.assertEqual(
            state.conclusion,
            "The hit rate is moderate; comparing more cache settings may be useful.",
        )

    def test_clear_restores_initial_state(self):
        self.controller.run(
            "Sequential GUI Experiment",
            self.config,
            "sequential",
            {"count": 8},
        )

        state = self.controller.clear()

        self.assertIsNone(state.summary)
        self.assertEqual(state.access_log, ())
        self.assertFalse(state.has_exportable_result)

    def test_csv_and_markdown_export_preserve_fields_and_titles(self):
        self.controller.run(
            "Sequential GUI Experiment",
            self.config,
            "sequential",
            {"count": 8},
        )

        with tempfile.TemporaryDirectory() as directory:
            csv_path, report_path = self.controller.export(directory)
            csv_text = csv_path.read_text(encoding="utf-8")
            report_text = report_path.read_text(encoding="utf-8")

        self.assertEqual(csv_path.name, "sequential_gui_experiment_access_log.csv")
        self.assertEqual(report_path.name, "sequential_gui_experiment_report.md")
        self.assertTrue(csv_text.startswith(
            "access_id,address,operation,tag,index,offset,hit,"
            "victim_way,replaced_valid,replaced_tag"
        ))
        self.assertIn("# Sequential GUI Experiment", report_text)
        self.assertIn("## Cache Configuration", report_text)
        self.assertIn("## Statistics", report_text)
        self.assertIn("## Conclusion", report_text)


if __name__ == "__main__":
    unittest.main()
