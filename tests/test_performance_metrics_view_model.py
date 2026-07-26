import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.performance import (
    PerformanceRunner,
    PerformanceTimingModel,
    build_metrics_view_model,
)


class PerformanceMetricsViewModelTest(unittest.TestCase):
    def metrics(self, addresses=(0, 4, 0)):
        return PerformanceRunner().run(
            CacheConfig(8, 4, 1, "LRU"),
            addresses,
            PerformanceTimingModel(1, 10, 0.5),
        ).metrics

    def test_all_raw_fields_map_exactly_without_rounding(self):
        metrics = self.metrics()
        view = build_metrics_view_model(metrics)
        for name in (
            "accesses", "hits", "misses", "hit_rate", "miss_rate",
            "hit_time_cycles", "effective_miss_penalty_cycles",
            "total_lookup_cycles", "total_miss_penalty_cycles",
            "total_cycles", "amat_cycles", "line_fills", "bytes_fetched",
            "bytes_fetched_per_access", "miss_stall_fraction",
        ):
            self.assertEqual(getattr(metrics, name), getattr(view, name), name)
        self.assertEqual(1 / 3, view.hit_rate)

    def test_all_four_invariants_are_true(self):
        view = build_metrics_view_model(self.metrics())
        self.assertTrue(view.access_invariant_ok)
        self.assertTrue(view.cycle_decomposition_ok)
        self.assertTrue(view.amat_invariant_ok)
        self.assertTrue(view.traffic_invariant_ok)

    def test_empty_trace_preserves_none_and_na_display(self):
        view = build_metrics_view_model(self.metrics(()))
        self.assertIsNone(view.amat_cycles)
        self.assertIsNone(view.bytes_fetched_per_access)
        self.assertIsNone(view.miss_stall_fraction)
        self.assertEqual("N/A", view.amat_display)
        self.assertEqual("N/A", view.bytes_per_access_display)
        self.assertEqual("N/A", view.miss_stall_fraction_display)

    def test_non_empty_display_preserves_value_string(self):
        view = build_metrics_view_model(self.metrics())
        self.assertEqual(str(view.amat_cycles), view.amat_display)
        self.assertEqual(str(view.bytes_fetched_per_access), view.bytes_per_access_display)
        self.assertEqual(str(view.miss_stall_fraction), view.miss_stall_fraction_display)

    def test_builder_requires_formal_metrics(self):
        with self.assertRaises(TypeError):
            build_metrics_view_model(object())


if __name__ == "__main__":
    unittest.main()
