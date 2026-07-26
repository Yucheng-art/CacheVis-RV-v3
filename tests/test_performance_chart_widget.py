from dataclasses import replace
import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from PySide6.QtWidgets import QApplication

from cachevis_rv.labs.performance import CAPACITY_KNEE_SWEEP, PerformanceChartMetric
from cachevis_rv.labs.performance.widget import PerformanceLabWidget


class PerformanceChartWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widget = PerformanceLabWidget()
        self.assertTrue(self.widget.run_sweep())

    def tearDown(self):
        self.widget.close()

    def test_seven_metrics_switch_without_rerunning(self):
        result = self.widget.controller.state.sweep_result
        for index, metric in enumerate(PerformanceChartMetric):
            self.widget.chart_panel.metric_combo.setCurrentIndex(index)
            self.assertIs(metric, self.widget.controller.state.chart_metric)
            self.assertIs(result, self.widget.controller.state.sweep_result)

    def test_order_baseline_selected_and_all_best_ties_are_preserved(self):
        state = self.widget.controller.state
        self.assertEqual(tuple(point.point_id for point in state.chart_series.points), ("cache_8", "cache_16", "cache_32"))
        self.assertEqual(("cache_16", "cache_32"), state.chart_series.best_point_ids)
        self.assertTrue(self.widget.select_point("cache_32"))
        selected = next(point for point in self.widget.controller.state.chart_series.points if point.is_selected)
        self.assertEqual("cache_32", selected.point_id)
        self.assertEqual(("cache_16", "cache_32"), self.widget.controller.state.chart_series.best_point_ids)

    def test_none_single_point_and_same_x_render_without_error(self):
        empty = replace(CAPACITY_KNEE_SWEEP, sweep_id="empty", addresses=())
        state = self.widget.controller.run_sweep(empty)
        self.widget._render(state)
        self.assertTrue(state.chart_series.has_missing_values)
        one = replace(CAPACITY_KNEE_SWEEP, sweep_id="one", points=(CAPACITY_KNEE_SWEEP.points[0],), baseline_point_id="cache_8")
        self.widget._render(self.widget.controller.run_sweep(one))
        same_x_points = tuple(replace(point, x_value=1) for point in CAPACITY_KNEE_SWEEP.points)
        same_x = replace(CAPACITY_KNEE_SWEEP, sweep_id="same_x", kind=CAPACITY_KNEE_SWEEP.kind, points=same_x_points)
        self.widget._render(self.widget.controller.run_sweep(same_x))
        self.widget.chart_panel.canvas.resize(640, 300)
        self.widget.chart_panel.canvas.grab()


if __name__ == "__main__":
    unittest.main()
