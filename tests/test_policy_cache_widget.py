import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.policy import POLICY_PRESETS
from cachevis_rv.labs.policy.widget import PolicyLabWidget


class PolicyCacheWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PolicyLabWidget()
        self.widget._show_error = lambda _message: None

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def _select(self, preset_id):
        index = next(i for i, preset in enumerate(POLICY_PRESETS) if preset.preset_id == preset_id)
        self.widget.controls.preset_combo.setCurrentIndex(index)

    def test_three_uniform_cache_lanes_start_invalid(self):
        self.assertTrue(self.widget.reset_experiment())
        self.assertEqual(("LRU", "FIFO", "Random"), tuple(self.widget.cache_panel.lane_panels))
        for lane in self.widget.controller.state.lane_caches:
            self.assertTrue(all(not line.valid for line in lane.cache_lines))

    def test_fill_hit_victim_candidate_and_changed_badges_render(self):
        self._select("victim_divergence_before_outcome")
        self.assertTrue(self.widget.step_experiment())
        for panel in self.widget.cache_panel.lane_panels.values():
            self.assertIn("FILL", panel.line_cards[0].property("badges"))
            self.assertIn("CHANGED", panel.line_cards[0].property("badges"))
        self.widget.run_all_experiment()
        for panel in self.widget.cache_panel.lane_panels.values():
            badges = [badge for card in panel.line_cards for badge in card.property("badges")]
            self.assertIn("VICTIM", badges)
            self.assertIn("VALID CANDIDATE", badges)
            self.assertIn("ELIGIBLE VICTIM", badges)

    def test_direct_mapped_has_one_eligible_candidate_per_lane(self):
        self._select("direct_mapped_control")
        self.widget.run_all_experiment()
        for lane in self.widget.controller.state.lane_caches:
            self.assertEqual(1, sum(line.is_eligible_victim for line in lane.cache_lines))

    def test_historical_selection_does_not_rebuild_latest_cache(self):
        self._select("lru_advantage")
        self.widget.run_all_experiment()
        before = self.widget.controller.state.lane_caches
        self.widget.select_timeline_step(0)
        self.assertEqual(before, self.widget.controller.state.lane_caches)


if __name__ == "__main__":
    unittest.main()
