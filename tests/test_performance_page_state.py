import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import (
    ANALYTICAL_L1_L2_MODEL,
    EMPTY_PERFORMANCE_PAGE_STATE,
    PERFORMANCE_SWEEP_PRESETS,
    PerformanceChartMetric,
    PerformanceController,
)


class PerformancePageStateTest(unittest.TestCase):
    def test_initial_state_is_empty_and_sequences_are_tuples(self):
        state = EMPTY_PERFORMANCE_PAGE_STATE
        self.assertFalse(state.has_sweep_result)
        self.assertFalse(state.has_hierarchy_result)
        self.assertIsNone(state.sweep_result)
        self.assertIsNone(state.hierarchy_result)
        self.assertEqual((), state.point_view_models)
        self.assertIsInstance(state.available_chart_metrics, tuple)
        self.assertEqual(tuple(PerformanceChartMetric), state.available_chart_metrics)

    def test_state_is_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            EMPTY_PERFORMANCE_PAGE_STATE.has_sweep_result = True

    def test_completed_sweep_state_has_one_selected_baseline(self):
        state = PerformanceController().run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        self.assertTrue(state.has_sweep_result)
        self.assertEqual("cache_8", state.selected_point_id)
        self.assertEqual(1, sum(point.is_selected for point in state.point_view_models))
        self.assertEqual(state.selected_point_id, state.selected_point.point_id)

    def test_select_point_changes_only_selection_views(self):
        controller = PerformanceController()
        before = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        after = controller.select_point("cache_32")
        self.assertIs(before.sweep_result, after.sweep_result)
        self.assertIs(before.sweep_summary, after.sweep_summary)
        self.assertIs(before.comparison_view, after.comparison_view)
        self.assertEqual(before.chart_metric, after.chart_metric)
        self.assertNotEqual(before.selected_point_id, after.selected_point_id)
        self.assertNotEqual(before.chart_series, after.chart_series)

    def test_select_chart_changes_only_chart_fields(self):
        controller = PerformanceController()
        before = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        after = controller.select_chart_metric(PerformanceChartMetric.TOTAL_CYCLES)
        self.assertEqual(before.selected_point, after.selected_point)
        self.assertIs(before.sweep_result, after.sweep_result)
        self.assertIs(before.sweep_summary, after.sweep_summary)
        self.assertIs(before.comparison_view, after.comparison_view)
        self.assertNotEqual(before.chart_metric, after.chart_metric)

    def test_hierarchy_and_sweep_sequences_remain_tuples(self):
        controller = PerformanceController()
        state = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        state = controller.analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        self.assertIsInstance(state.point_view_models, tuple)
        self.assertIsInstance(state.chart_series.points, tuple)
        self.assertIsInstance(state.hierarchy_view.probability_rows, tuple)
        self.assertIsInstance(state.hierarchy_view.contribution_rows, tuple)
        self.assertIsInstance(state.hierarchy_view.rule_path, tuple)
        self.assertIsInstance(state.hierarchy_view.limitation_notes, tuple)


if __name__ == "__main__":
    unittest.main()
