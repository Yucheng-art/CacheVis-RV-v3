import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from PySide6.QtWidgets import QApplication
from cachevis_rv.labs.write_policy.widget import WritePolicyLabWidget


class WritePolicyDecisionWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def test_bypass_and_allocated_miss_render_as_miss_with_na(self):
        widget = WritePolicyLabWidget(); widget.controls.preset_combo.setCurrentIndex(2)
        self.assertTrue(widget.load_experiment()); self.assertTrue(widget.step())
        headings = tuple(card.heading.text() for card in widget.decision_panel.cards)
        bodies = tuple(card.body.text() for card in widget.decision_panel.cards)
        self.assertTrue(all("MISS" in text for text in headings))
        self.assertIn("Bypassed: Yes", bodies[1]); self.assertIn("Allocated: Yes", bodies[0])
        self.assertIn("N/A", bodies[1]); self.assertIn("Metadata consistent: Yes", bodies[0])
        widget.close()

    def test_historical_decision_changes_without_current_cache(self):
        widget = WritePolicyLabWidget(); widget.controls.preset_combo.setCurrentIndex(6)
        widget.load_experiment(); widget.run_all(); caches = widget.controller.state.current_lane_caches
        self.assertTrue(widget.select_step(0)); self.assertEqual(widget.controller.state.current_lane_caches, caches)
        self.assertTrue(widget.current_access_panel.history_notice.isVisibleTo(widget))
        widget.close()


if __name__ == "__main__": unittest.main()
