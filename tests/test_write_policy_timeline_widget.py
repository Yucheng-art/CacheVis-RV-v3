import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from PySide6.QtWidgets import QApplication
from cachevis_rv.labs.write_policy.widget import WritePolicyLabWidget


class WritePolicyTimelineWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def test_selection_latest_and_new_step_semantics(self):
        widget = WritePolicyLabWidget(); widget.controls.preset_combo.setCurrentIndex(6); widget.load_experiment()
        widget.step(); widget.step(); before = (widget.controller.state.current_lane_caches, widget.controller.state.current_lane_statistics, widget.controller.state.next_step_index)
        widget.timeline_panel._cell_clicked(0, 0)
        state = widget.controller.state
        self.assertEqual((state.selected_step_index, state.latest_step_index), (0, 1))
        self.assertEqual((state.current_lane_caches, state.current_lane_statistics, state.next_step_index), before)
        widget.step(); self.assertEqual(widget.controller.state.selected_step_index, 2)
        widget.reset_experiment(); self.assertEqual(widget.timeline_panel.table.rowCount(), 0)
        widget.close()

    def test_mixed_divergence_table_is_exact(self):
        widget = WritePolicyLabWidget(); widget.controls.preset_combo.setCurrentIndex(6); widget.load_experiment(); widget.run_all()
        self.assertEqual(tuple(widget.divergence_panel.table.item(row, 1).text() for row in range(7)),
                         ("1", "4", "3", "2", "5", "5", "5"))
        widget.close()


if __name__ == "__main__": unittest.main()
