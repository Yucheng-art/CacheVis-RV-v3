import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.policy import POLICY_PRESETS
from cachevis_rv.labs.policy.widget import PolicyLabWidget


class PolicyGuiViewModelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PolicyLabWidget()
        self.widget._show_error = lambda _message: None
        self.widget._show_information = lambda _title, _message: None

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def _run(self, preset_id):
        index = next(i for i, preset in enumerate(POLICY_PRESETS) if preset.preset_id == preset_id)
        self.widget.controls.preset_combo.setCurrentIndex(index)
        self.assertTrue(self.widget.run_all_experiment())
        return self.widget.controller.state

    def test_hit_and_invalid_fill_hide_inapplicable_victim_fields(self):
        state = self._run("no_replacement_pressure")
        self.widget.select_timeline_step(0)
        for panel in self.widget.decision_panel.lane_panels.values():
            self.assertIn("Fill way: 0", panel.facts_label.text())
            self.assertIn("Victim way: N/A", panel.facts_label.text())
        self.widget.select_timeline_step(2)
        for panel in self.widget.decision_panel.lane_panels.values():
            self.assertIn("Hit way: 0", panel.facts_label.text())
            self.assertIn("Fill way: N/A", panel.facts_label.text())
            self.assertIn("Victim way: N/A", panel.facts_label.text())
        self.assertEqual(4, state.statistics.accesses)

    def test_eviction_lanes_show_policy_specific_metadata(self):
        self._run("victim_divergence_before_outcome")
        lru = self.widget.decision_panel.lane_panels["LRU"].metadata_label.text()
        fifo = self.widget.decision_panel.lane_panels["FIFO"].metadata_label.text()
        random_text = self.widget.decision_panel.lane_panels["Random"].metadata_label.text()
        self.assertIn("LRU → MRU", lru)
        self.assertIn("Candidate last_used: way", lru)
        self.assertIn("Selected last_used", lru)
        self.assertIn("oldest → newest", fifo)
        self.assertIn("Candidate insert_time: way", fifo)
        self.assertIn("does not refresh insertion order", fifo)
        self.assertIn("Random candidates", random_text)
        self.assertIn("Seed:", random_text)
        self.assertIn("Random draw index", random_text)
        for forbidden in ("best", "oldest", "least-used"):
            self.assertNotIn(forbidden, random_text.lower())

    def test_divergence_panels_report_observed_timing_only(self):
        victim = self._run("victim_divergence_before_outcome")
        self.assertEqual(3, victim.divergence_summary.first_state_divergence_step)
        self.assertIsNone(victim.divergence_summary.first_outcome_divergence_step)
        self.assertEqual("Not yet", self.widget.divergence_panel.values["first_outcome"].text())
        lru = self._run("lru_advantage")
        self.assertTrue(lru.divergence_summary.state_before_outcome)
        self.assertEqual("1 step(s)", self.widget.divergence_panel.values["lag"].text())
        fifo = self._run("fifo_advantage")
        self.assertEqual(1, fifo.divergence_summary.divergence_lag_steps)

    def test_statistics_show_tie_and_trace_specific_leader(self):
        self._run("no_replacement_pressure")
        self.assertIn("tie", self.widget.statistics_panel.comparison_label.text().lower())
        self._run("lru_advantage")
        text = self.widget.statistics_panel.comparison_label.text()
        self.assertIn("Current trace leader: LRU", text)
        self.assertIn("does not imply universal superiority", text)

    def test_history_selection_only_changes_decisions_and_timeline_selection(self):
        state = self._run("lru_advantage")
        caches = state.lane_caches
        statistics = state.statistics_view
        divergence = state.divergence_summary
        self.widget.select_timeline_step(0)
        selected = self.widget.controller.state
        self.assertEqual(0, selected.selected_step.step_index)
        self.assertEqual(4, selected.current_step.step_index)
        self.assertEqual(caches, selected.lane_caches)
        self.assertEqual(statistics, selected.statistics_view)
        self.assertEqual(divergence, selected.divergence_summary)
        self.assertTrue(self.widget.timeline.chips[0].text().endswith("SELECTED"))
        self.assertIn("CURRENT", self.widget.timeline.chips[-1].text())


if __name__ == "__main__":
    unittest.main()
