"""Structure and compatibility tests for the extracted classic lab pages."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.compare_experiment import CompareExperimentWidget
from cachevis_rv.labs.compare_experiment.runner import (
    build_comparison_configs as package_build_comparison_configs,
    compare_cache_configs as package_compare_cache_configs,
    run_comparison as package_run_comparison,
)
from cachevis_rv.labs.single_experiment import SingleExperimentWidget
from cachevis_rv.labs.single_experiment.runner import (
    build_trace as package_build_trace,
    make_single_experiment_conclusion as package_make_conclusion,
    run_single_experiment as package_run_single_experiment,
)
from compare_runner import (
    build_comparison_configs as flat_build_comparison_configs,
    compare_cache_configs as flat_compare_cache_configs,
    run_comparison as flat_run_comparison,
)
from experiment_runner import (
    build_trace as flat_build_trace,
    make_single_experiment_conclusion as flat_make_conclusion,
    run_single_experiment as flat_run_single_experiment,
)


class ClassicLabPackageStructureTest(unittest.TestCase):
    def setUp(self):
        self.src = Path(__file__).resolve().parents[1] / "src"

    def test_widgets_import_from_new_packages(self):
        self.assertEqual(SingleExperimentWidget.__name__, "SingleExperimentWidget")
        self.assertEqual(CompareExperimentWidget.__name__, "CompareExperimentWidget")

    def test_app_window_is_a_lightweight_three_tab_shell(self):
        source = (self.src / "app_window.py").read_text(encoding="utf-8")

        self.assertNotIn("def _build_single_tab", source)
        self.assertNotIn("def _build_compare_tab", source)
        self.assertNotIn("def run_single_experiment", source)
        self.assertNotIn("def run_compare_experiment", source)
        self.assertNotIn("def export_current_report", source)
        self.assertNotIn("def export_compare_report", source)
        self.assertNotIn("CacheSimulator", source)

    def test_app_window_preserves_tab_names_and_order(self):
        source = (self.src / "app_window.py").read_text(encoding="utf-8")
        labels = [
            '"Address Visualizer"',
            '"Single Experiment"',
            '"Compare Experiment"',
        ]

        positions = [source.index(label) for label in labels]

        self.assertEqual(positions, sorted(positions))

    def test_only_widgets_import_pyside6(self):
        for lab in ("single_experiment", "compare_experiment"):
            package = self.src / "cachevis_rv" / "labs" / lab
            for name in ("controller.py", "view_model.py", "runner.py"):
                with self.subTest(lab=lab, name=name):
                    self.assertNotIn(
                        "PySide6",
                        (package / name).read_text(encoding="utf-8"),
                    )
            self.assertIn(
                "PySide6",
                (package / "widget.py").read_text(encoding="utf-8"),
            )

    def test_flat_runner_facades_keep_object_identity(self):
        self.assertIs(flat_build_trace, package_build_trace)
        self.assertIs(flat_run_single_experiment, package_run_single_experiment)
        self.assertIs(flat_make_conclusion, package_make_conclusion)
        self.assertIs(flat_compare_cache_configs, package_compare_cache_configs)
        self.assertIs(
            flat_build_comparison_configs,
            package_build_comparison_configs,
        )
        self.assertIs(flat_run_comparison, package_run_comparison)


if __name__ == "__main__":
    unittest.main()
