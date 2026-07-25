"""Structure and offscreen interaction tests for Miss Type Lab."""

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication, QScrollArea

from cachevis_rv.labs.miss_type.widget import MissTypeLabWidget


class MissTypeWidgetStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = MissTypeLabWidget()

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def test_page_is_overall_scroll_area_with_split_subcomponents(self):
        self.assertIsInstance(self.widget, QScrollArea)
        self.assertIsNotNone(self.widget.controls)
        self.assertIsNotNone(self.widget.current_panel)
        self.assertIsNotNone(self.widget.actual_cache_panel)
        self.assertIsNotNone(self.widget.reference_cache_panel)
        self.assertIsNotNone(self.widget.evidence_panel)
        self.assertIsNotNone(self.widget.statistics_panel)
        self.assertIsNotNone(self.widget.timeline)

    def test_three_presets_fill_inputs_without_running(self):
        self.assertEqual(self.widget.controls.preset_combo.count(), 3)
        for index in range(3):
            self.widget.controls.preset_combo.setCurrentIndex(index)
            self.app.processEvents()
            self.assertTrue(self.widget.controls.trace_input.toPlainText())
            self.assertFalse(self.widget.controller.state.has_session)

    def test_reset_step_run_all_and_history_selection(self):
        self.assertTrue(self.widget.reset_experiment())
        self.assertTrue(self.widget.step_experiment())
        self.assertEqual(self.widget.controller.state.current_step.step_index, 0)
        self.assertTrue(self.widget.run_all_experiment())
        latest = self.widget.controller.state
        actual_lines = latest.actual_cache_lines
        reference_lines = latest.reference_cache_lines
        statistics = latest.statistics

        self.assertTrue(self.widget.select_timeline_step(0))
        selected = self.widget.controller.state
        self.assertEqual(selected.selected_step.step_index, 0)
        self.assertIs(selected.actual_cache_lines, actual_lines)
        self.assertIs(selected.reference_cache_lines, reference_lines)
        self.assertIs(selected.statistics, statistics)

    def test_widget_does_not_call_session_simulator_or_classifier(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "miss_type"
            / "widgets" / "lab_widget.py"
        ).read_text(encoding="utf-8")
        for forbidden in ("MissTypeSession", "CacheSimulator", "MissTypeClassifier"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_semantic_light_surfaces_use_explicit_dark_text(self):
        package = (
            Path(__file__).resolve().parents[1]
            / "src" / "cachevis_rv" / "labs" / "miss_type" / "widgets"
        )
        source = "\n".join(
            (package / name).read_text(encoding="utf-8")
            for name in ("cache_panel.py", "evidence_panel.py", "timeline.py")
        )
        for dark_color in ("#14532d", "#173f73", "#713600", "#7f1d1d"):
            self.assertIn(dark_color, source)


if __name__ == "__main__":
    unittest.main()
