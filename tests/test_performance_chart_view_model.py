import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.performance import (
    CAPACITY_KNEE_SWEEP,
    PerformanceChartMetric,
    PerformanceRunSpec,
    PerformanceSweepDefinition,
    PerformanceSweepKind,
    PerformanceSweepRunner,
    PerformanceTimingModel,
    build_chart_series_view_model,
)


class PerformanceChartViewModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = PerformanceSweepRunner().run(CAPACITY_KNEE_SWEEP)

    def test_every_metric_maps_values_without_sorting(self):
        mappings = {
            PerformanceChartMetric.AMAT: lambda p: p.run_result.metrics.amat_cycles,
            PerformanceChartMetric.HIT_RATE: lambda p: p.run_result.metrics.hit_rate,
            PerformanceChartMetric.MISS_RATE: lambda p: p.run_result.metrics.miss_rate,
            PerformanceChartMetric.TOTAL_CYCLES: lambda p: p.run_result.metrics.total_cycles,
            PerformanceChartMetric.BYTES_FETCHED: lambda p: p.run_result.metrics.bytes_fetched,
            PerformanceChartMetric.MISS_STALL_FRACTION: lambda p: p.run_result.metrics.miss_stall_fraction,
            PerformanceChartMetric.SPEEDUP: lambda p: p.speedup_vs_baseline,
        }
        for metric, getter in mappings.items():
            with self.subTest(metric=metric):
                series = build_chart_series_view_model(self.result, metric, "cache_32")
                self.assertEqual(tuple(p.point_id for p in self.result.point_results), tuple(p.point_id for p in series.points))
                self.assertEqual(tuple(getter(p) for p in self.result.point_results), tuple(p.y_value for p in series.points))

    def test_baseline_and_selected_markers_are_independent(self):
        series = build_chart_series_view_model(self.result, PerformanceChartMetric.AMAT, "cache_32")
        self.assertTrue(series.points[0].is_baseline)
        self.assertFalse(series.points[0].is_selected)
        self.assertFalse(series.points[2].is_baseline)
        self.assertTrue(series.points[2].is_selected)

    def test_best_direction_and_ties_are_correct(self):
        expected = {
            PerformanceChartMetric.AMAT: ("cache_16", "cache_32"),
            PerformanceChartMetric.HIT_RATE: ("cache_16", "cache_32"),
            PerformanceChartMetric.MISS_RATE: ("cache_16", "cache_32"),
            PerformanceChartMetric.TOTAL_CYCLES: ("cache_16", "cache_32"),
            PerformanceChartMetric.BYTES_FETCHED: ("cache_16", "cache_32"),
            PerformanceChartMetric.MISS_STALL_FRACTION: ("cache_16", "cache_32"),
            PerformanceChartMetric.SPEEDUP: ("cache_16", "cache_32"),
        }
        for metric, ids in expected.items():
            with self.subTest(metric=metric):
                series = build_chart_series_view_model(self.result, metric, "cache_8")
                self.assertEqual(ids, series.best_point_ids)
                self.assertEqual(ids, tuple(p.point_id for p in series.points if p.is_best_for_metric))

    def test_empty_trace_retains_none_points_and_has_no_amat_best(self):
        definition = PerformanceSweepDefinition(
            "empty", "Empty", "Empty trace.", PerformanceSweepKind.CUSTOM, (),
            (
                PerformanceRunSpec("a", "A", 1, CacheConfig(8, 4, 1, "LRU"), PerformanceTimingModel(1, 10, 0)),
                PerformanceRunSpec("b", "B", 2, CacheConfig(8, 4, 1, "LRU"), PerformanceTimingModel(2, 10, 0)),
            ),
            "a", "Empty trace semantics.",
        )
        result = PerformanceSweepRunner().run(definition)
        series = build_chart_series_view_model(result, PerformanceChartMetric.AMAT, "a")
        self.assertEqual(2, len(series.points))
        self.assertEqual((None, None), tuple(point.y_value for point in series.points))
        self.assertTrue(series.has_missing_values)
        self.assertEqual((), series.best_point_ids)

    def test_x_axis_labels_cover_all_sweep_kinds(self):
        expected = {
            PerformanceSweepKind.CACHE_SIZE: "Cache Size (bytes)",
            PerformanceSweepKind.BLOCK_SIZE: "Block Size (bytes)",
            PerformanceSweepKind.ASSOCIATIVITY: "Associativity (ways)",
            PerformanceSweepKind.MISS_PENALTY: "Fixed Miss Overhead (cycles)",
            PerformanceSweepKind.HIT_TIME: "Hit Time (cycles)",
            PerformanceSweepKind.CUSTOM: "Sweep Value",
        }
        base = CAPACITY_KNEE_SWEEP
        for kind, label in expected.items():
            definition = PerformanceSweepDefinition(
                f"axis_{kind.value}", "Axis", "Axis label.", kind,
                base.addresses, (base.points[0],), base.points[0].point_id, "Axis.",
            )
            result = PerformanceSweepRunner().run(definition)
            series = build_chart_series_view_model(result, PerformanceChartMetric.AMAT, base.points[0].point_id)
            self.assertEqual(label, series.x_axis_label)

    def test_invalid_metric_is_rejected(self):
        with self.assertRaises(ValueError):
            build_chart_series_view_model(self.result, "AMAT", "cache_8")


if __name__ == "__main__":
    unittest.main()
