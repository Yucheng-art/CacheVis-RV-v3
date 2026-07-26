import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.performance.widget import PerformanceLabWidget


class PerformanceSweepTableWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PerformanceLabWidget()

    def tearDown(self):
        self.widget.close()

    def test_all_presets_render_definition_order_and_formal_rows(self):
        for index in range(6):
            self.widget.controls.preset_combo.setCurrentIndex(index)
            self.assertTrue(self.widget.run_sweep())
            state = self.widget.controller.state
            self.assertEqual(self.widget.sweep_table.rowCount(), len(state.point_view_models))
            self.assertEqual(
                tuple(self.widget.sweep_table.item(row, 0).text() for row in range(self.widget.sweep_table.rowCount())),
                tuple(point.label for point in state.point_view_models),
            )

    def test_row_selection_changes_only_selected_views(self):
        self.assertTrue(self.widget.run_sweep())
        before = self.widget.controller.state
        self.widget.sweep_table._select_row(2, 0)
        after = self.widget.controller.state
        self.assertEqual("cache_32", after.selected_point_id)
        self.assertIs(before.sweep_result, after.sweep_result)
        self.assertIs(before.sweep_summary, after.sweep_summary)
        self.assertIs(before.comparison_view, after.comparison_view)
        self.assertTrue(after.point_view_models[0].is_baseline)
        self.assertFalse(after.point_view_models[0].is_selected)

    def test_empty_trace_shows_na_and_invariants(self):
        self.widget.controls.trace_input.clear()
        self.assertTrue(self.widget.run_sweep())
        self.assertEqual("N/A", self.widget.sweep_table.item(0, 12).text())
        metrics = self.widget.controller.state.selected_point.metrics
        self.assertIsNone(metrics.amat_cycles)
        self.assertTrue(metrics.access_invariant_ok)
        self.assertEqual("N/A", self.widget.selected_point_panel.metrics_panel.labels["AMAT"].text())

    def test_hit_rate_reversal_values_are_visible(self):
        self.widget.controls.preset_combo.setCurrentIndex(5)
        self.assertTrue(self.widget.run_sweep())
        state = self.widget.controller.state
        self.assertEqual(("slow_large",), state.sweep_summary.best_hit_rate_point_ids)
        self.assertEqual(("fast_small",), state.sweep_summary.best_amat_point_ids)
        text = self.widget.comparison_panel.pairs.text()
        self.assertIn("hit rate 0.5", text)
        self.assertIn("AMAT 13.0", text)
        self.assertIn("AMAT 11.0", text)


if __name__ == "__main__":
    unittest.main()
