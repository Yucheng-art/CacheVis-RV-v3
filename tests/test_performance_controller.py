import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import (
    ANALYTICAL_L1_L2_MODEL,
    PERFORMANCE_SWEEP_PRESETS,
    PerformanceChartMetric,
    PerformanceController,
    PerformanceSweepRunner,
    TwoLevelPerformanceAnalyzer,
)


class SpySweepRunner:
    def __init__(self):
        self.calls = 0
        self.runner = PerformanceSweepRunner()

    def run(self, definition):
        self.calls += 1
        return self.runner.run(definition)


class SpyHierarchyAnalyzer:
    def __init__(self):
        self.calls = 0

    def analyze(self, model):
        self.calls += 1
        return TwoLevelPerformanceAnalyzer.analyze(model)


class PerformanceControllerTest(unittest.TestCase):
    def test_all_six_sweep_presets_run(self):
        controller = PerformanceController()
        self.assertEqual(6, len(PERFORMANCE_SWEEP_PRESETS))
        for definition in PERFORMANCE_SWEEP_PRESETS:
            with self.subTest(sweep=definition.sweep_id):
                state = controller.run_sweep(definition)
                self.assertTrue(state.has_sweep_result)
                self.assertEqual(definition.baseline_point_id, state.selected_point_id)

    def test_hierarchy_preset_runs(self):
        state = PerformanceController().analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        self.assertTrue(state.has_hierarchy_result)
        self.assertEqual(3.8, state.hierarchy_view.amat_cycles)

    def test_run_sweep_defaults_to_baseline_and_amat_chart(self):
        definition = PERFORMANCE_SWEEP_PRESETS[0]
        state = PerformanceController().run_sweep(definition)
        self.assertEqual(definition.baseline_point_id, state.selected_point_id)
        self.assertTrue(state.selected_point.is_baseline)
        self.assertTrue(state.selected_point.is_selected)
        self.assertEqual(PerformanceChartMetric.AMAT, state.chart_metric)

    def test_select_point_does_not_rerun_sweep_or_change_domain_result(self):
        spy = SpySweepRunner()
        controller = PerformanceController(sweep_runner=spy)
        state = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        result = state.sweep_result
        summary = state.sweep_summary
        comparison = state.comparison_view
        state = controller.select_point("cache_32")
        self.assertEqual(1, spy.calls)
        self.assertIs(result, state.sweep_result)
        self.assertIs(summary, state.sweep_summary)
        self.assertIs(comparison, state.comparison_view)
        self.assertEqual("cache_32", state.selected_point_id)
        self.assertEqual(1, sum(point.is_selected for point in state.point_view_models))

    def test_unknown_point_id_is_rejected(self):
        controller = PerformanceController()
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        with self.assertRaisesRegex(ValueError, "unknown performance point_id"):
            controller.select_point("missing")

    def test_select_chart_metric_does_not_rerun_sweep(self):
        spy = SpySweepRunner()
        controller = PerformanceController(sweep_runner=spy)
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        result = controller.state.sweep_result
        state = controller.select_chart_metric(PerformanceChartMetric.HIT_RATE)
        self.assertEqual(1, spy.calls)
        self.assertIs(result, state.sweep_result)
        self.assertEqual(PerformanceChartMetric.HIT_RATE, state.chart_metric)

    def test_invalid_chart_metric_is_rejected(self):
        controller = PerformanceController()
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        with self.assertRaisesRegex(ValueError, "PerformanceChartMetric"):
            controller.select_chart_metric("amat")

    def test_sweep_and_hierarchy_results_are_independent(self):
        controller = PerformanceController()
        sweep_state = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        sweep_result = sweep_state.sweep_result
        hierarchy_state = controller.analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        self.assertIs(sweep_result, hierarchy_state.sweep_result)
        hierarchy_result = hierarchy_state.hierarchy_result
        rerun = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[1])
        self.assertIs(hierarchy_result, rerun.hierarchy_result)

    def test_clear_sweep_preserves_hierarchy(self):
        controller = PerformanceController()
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        controller.analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        hierarchy = controller.state.hierarchy_result
        state = controller.clear_sweep()
        self.assertFalse(state.has_sweep_result)
        self.assertTrue(state.has_hierarchy_result)
        self.assertIs(hierarchy, state.hierarchy_result)

    def test_clear_hierarchy_preserves_sweep(self):
        controller = PerformanceController()
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        sweep = controller.state.sweep_result
        controller.analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        state = controller.clear_hierarchy()
        self.assertTrue(state.has_sweep_result)
        self.assertFalse(state.has_hierarchy_result)
        self.assertIs(sweep, state.sweep_result)

    def test_clear_all_returns_empty_state(self):
        controller = PerformanceController()
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        controller.analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        state = controller.clear_all()
        self.assertFalse(state.has_sweep_result)
        self.assertFalse(state.has_hierarchy_result)

    def test_repeated_runs_are_equal(self):
        controller = PerformanceController()
        first = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0]).sweep_result
        second = controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0]).sweep_result
        self.assertEqual(first, second)

    def test_selection_requires_a_completed_sweep(self):
        controller = PerformanceController()
        with self.assertRaises(RuntimeError):
            controller.select_point("anything")
        with self.assertRaises(RuntimeError):
            controller.select_chart_metric(PerformanceChartMetric.AMAT)

    def test_injected_analyzer_is_called_only_by_analysis(self):
        spy = SpyHierarchyAnalyzer()
        controller = PerformanceController(hierarchy_analyzer=spy)
        controller.run_sweep(PERFORMANCE_SWEEP_PRESETS[0])
        controller.select_point("cache_16")
        self.assertEqual(0, spy.calls)
        controller.analyze_hierarchy(ANALYTICAL_L1_L2_MODEL)
        self.assertEqual(1, spy.calls)


if __name__ == "__main__":
    unittest.main()
