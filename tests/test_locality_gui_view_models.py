"""Offscreen rendering semantics for Locality panels."""

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.locality import (
    FIXED_STRIDE,
    LOOP_TEMPORAL_REUSE,
    LocalityKind,
)
from cachevis_rv.labs.locality.widget import LocalityLabWidget


class LocalityGuiViewModelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = LocalityLabWidget()
        self.widget._show_error = lambda _message: None
        self.widget._show_information = lambda _title, _message: None

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def apply(self, preset):
        index = self.widget.controls.preset_combo.findData(preset)
        self.widget.controls.preset_combo.setCurrentIndex(index)

    def test_initial_and_latest_current_access_status(self):
        self.assertEqual(self.widget.current_panel.status_label.text(), "Ready")
        self.assertTrue(self.widget.reset_experiment())
        self.assertEqual(
            self.widget.current_panel.status_label.text(), "Awaiting first access"
        )
        self.assertTrue(self.widget.step_experiment())
        self.assertEqual(
            self.widget.current_panel.status_label.text(), "Latest execution"
        )
        self.assertEqual(self.widget.current_panel.values["kind"].text(), "First Touch")

    def test_evidence_f_s_t_and_cache_are_independent(self):
        self.apply(LOOP_TEMPORAL_REUSE)
        self.widget.run_all_experiment()
        self.assertIs(
            self.widget.controller.state.selected_step.locality_kind,
            LocalityKind.TEMPORAL,
        )
        self.assertEqual(
            self.widget.evidence_panel.title_label.text(), "Temporal Locality"
        )
        self.assertIn("CACHE HIT", self.widget.evidence_panel.cache_badge.text())
        self.assertIn(
            "does not guarantee", self.widget.evidence_panel.insight_label.text()
        )

    def test_no_reuse_samples_render_as_na(self):
        self.apply(FIXED_STRIDE)
        self.widget.run_all_experiment()
        values = self.widget.statistics_panel.values
        self.assertEqual(values["average_address_reuse_gap"].text(), "N/A")
        self.assertEqual(values["average_block_reuse_gap"].text(), "N/A")
        self.assertEqual(values["average_block_reuse_distance"].text(), "N/A")

    def test_historical_selection_updates_evidence_only(self):
        self.apply(LOOP_TEMPORAL_REUSE)
        self.widget.run_all_experiment()
        latest = self.widget.controller.state
        self.widget.select_timeline_step(0)
        selected = self.widget.controller.state
        self.assertIs(selected.current_step, latest.current_step)
        self.assertEqual(selected.selected_step.step_index, 0)
        self.assertIs(selected.cache_lines, latest.cache_lines)
        self.assertIs(selected.statistics, latest.statistics)
        self.assertIs(selected.block_access_cells, latest.block_access_cells)
        self.assertEqual(
            self.widget.evidence_panel.title_label.text(), "First Touch"
        )

    def test_timeline_chip_click_selects_history_but_keeps_current(self):
        self.apply(LOOP_TEMPORAL_REUSE)
        self.widget.run_all_experiment()
        self.widget.timeline.chips[0].click()
        self.app.processEvents()
        state = self.widget.controller.state
        self.assertEqual(state.current_step.step_index, 7)
        self.assertEqual(state.selected_step.step_index, 0)
        self.assertTrue(state.timeline_items[7].is_current)
        self.assertTrue(state.timeline_items[0].is_selected)

    def test_light_semantic_surfaces_use_dark_text(self):
        sources = (
            self.widget.evidence_panel.card.styleSheet(),
            self.widget.concept_note.styleSheet(),
        )
        for style in sources:
            self.assertIn("color:", style)
            self.assertNotIn("color: #fff", style.lower())


if __name__ == "__main__":
    unittest.main()
