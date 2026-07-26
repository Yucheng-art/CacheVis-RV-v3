import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.performance import (
    PERFORMANCE_SWEEP_PRESETS,
    PerformanceRunner,
    PerformanceSweepRunner,
    PerformanceTimingModel,
)


class PerformanceInvariantsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sweeps = tuple(
            PerformanceSweepRunner().run(definition)
            for definition in PERFORMANCE_SWEEP_PRESETS
        )

    def test_cycle_decomposition_and_amat_hold_for_all_presets(self):
        for sweep in self.sweeps:
            for point in sweep.point_results:
                metrics = point.run_result.metrics
                with self.subTest(sweep=sweep.definition.sweep_id, point=point.point_id):
                    self.assertTrue(math.isclose(metrics.total_cycles, metrics.total_lookup_cycles + metrics.total_miss_penalty_cycles))
                    self.assertTrue(math.isclose(metrics.amat_cycles * metrics.accesses, metrics.total_cycles))

    def test_count_rate_and_traffic_invariants_hold_for_all_presets(self):
        for sweep in self.sweeps:
            for point in sweep.point_results:
                metrics = point.run_result.metrics
                with self.subTest(sweep=sweep.definition.sweep_id, point=point.point_id):
                    self.assertEqual(metrics.accesses, metrics.hits + metrics.misses)
                    self.assertEqual(metrics.misses, metrics.line_fills)
                    self.assertEqual(metrics.misses * point.run_result.config.block_size_bytes, metrics.bytes_fetched)
                    self.assertTrue(0 <= metrics.hit_rate <= 1)
                    self.assertTrue(0 <= metrics.miss_rate <= 1)

    def test_all_numeric_results_are_finite_or_explicit_none(self):
        for sweep in self.sweeps:
            for point in sweep.point_results:
                for value in vars(point.run_result.metrics).values():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        self.assertTrue(math.isfinite(value))
                for value in (point.amat_delta_vs_baseline, point.speedup_vs_baseline):
                    self.assertTrue(value is None or math.isfinite(value))

    def test_baseline_relations_are_consistent(self):
        for sweep in self.sweeps:
            baseline = next(p for p in sweep.point_results if p.point_id == sweep.baseline_point_id)
            self.assertEqual(0.0, baseline.amat_delta_vs_baseline)
            self.assertEqual(0.0, baseline.total_cycles_delta_vs_baseline)
            self.assertEqual(1.0, baseline.speedup_vs_baseline)

    def test_empty_trace_semantics_are_consistent(self):
        metrics = PerformanceRunner().run(
            CacheConfig(8, 4, 1, "LRU"),
            (),
            PerformanceTimingModel(1, 20, 0.5),
        ).metrics
        self.assertEqual(0.0, metrics.hit_rate)
        self.assertEqual(0.0, metrics.miss_rate)
        self.assertEqual(0.0, metrics.total_cycles)
        self.assertIsNone(metrics.amat_cycles)
        self.assertIsNone(metrics.bytes_fetched_per_access)
        self.assertIsNone(metrics.miss_stall_fraction)

    def test_miss_penalty_is_extra_to_every_access_lookup(self):
        metrics = PerformanceRunner().run(
            CacheConfig(8, 4, 1, "LRU"),
            (0, 4, 0, 4),
            PerformanceTimingModel(3, 10, 0),
        ).metrics
        self.assertEqual(4 * 3, metrics.total_lookup_cycles)
        self.assertEqual(2 * 10, metrics.total_miss_penalty_cycles)


if __name__ == "__main__":
    unittest.main()
