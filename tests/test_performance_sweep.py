import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.performance import (
    PerformanceRunSpec,
    PerformanceSweepDefinition,
    PerformanceSweepKind,
    PerformanceSweepRunner,
    PerformanceTimingModel,
)


def point(point_id, config=None, timing=None, x=0):
    return PerformanceRunSpec(
        point_id,
        point_id,
        x,
        config or CacheConfig(8, 4, 1, "LRU"),
        timing or PerformanceTimingModel(1, 10, 0),
    )


def definition(kind, points, addresses=(0, 4, 0, 4), baseline=None):
    return PerformanceSweepDefinition(
        "test",
        "Test sweep",
        "A test sweep.",
        kind,
        addresses,
        tuple(points),
        baseline or points[0].point_id,
        "A stable teaching conclusion.",
    )


class PerformanceSweepTest(unittest.TestCase):
    def test_point_order_and_common_trace_are_preserved(self):
        result = PerformanceSweepRunner().run(definition(
            PerformanceSweepKind.CUSTOM,
            [point("second", x=2), point("first", x=1)],
        ))
        self.assertEqual(("second", "first"), tuple(p.point_id for p in result.point_results))
        self.assertTrue(all(p.run_result.addresses == (0, 4, 0, 4) for p in result.point_results))

    def test_duplicate_point_id_and_missing_baseline_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            definition(PerformanceSweepKind.CUSTOM, [point("a"), point("a")])
        with self.assertRaisesRegex(ValueError, "baseline"):
            definition(PerformanceSweepKind.CUSTOM, [point("a")], baseline="missing")

    def test_baseline_deltas_and_speedup_direction(self):
        fast = point("fast", timing=PerformanceTimingModel(1, 1, 0))
        slow = point("slow", timing=PerformanceTimingModel(2, 10, 0))
        result = PerformanceSweepRunner().run(definition(PerformanceSweepKind.CUSTOM, [fast, slow]))
        baseline, current = result.point_results
        self.assertEqual((0.0, 0.0, 1.0), (
            baseline.amat_delta_vs_baseline,
            baseline.total_cycles_delta_vs_baseline,
            baseline.speedup_vs_baseline,
        ))
        self.assertGreater(current.amat_delta_vs_baseline, 0)
        self.assertGreater(current.total_cycles_delta_vs_baseline, 0)
        self.assertLess(current.speedup_vs_baseline, 1)
        self.assertTrue(math.isclose(
            current.speedup_vs_baseline,
            baseline.run_result.metrics.total_cycles / current.run_result.metrics.total_cycles,
        ))

    def test_empty_trace_speedup_and_amat_delta_are_none(self):
        result = PerformanceSweepRunner().run(definition(
            PerformanceSweepKind.CUSTOM,
            [point("a"), point("b")],
            addresses=(),
        ))
        for item in result.point_results:
            self.assertIsNone(item.speedup_vs_baseline)
            self.assertIsNone(item.amat_delta_vs_baseline)

    def test_cache_size_sweep_rejects_other_config_change(self):
        points = [point("a"), point("b", CacheConfig(16, 8, 1, "LRU"))]
        with self.assertRaisesRegex(ValueError, "cache_size_bytes"):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.CACHE_SIZE, points))

    def test_cache_size_sweep_rejects_timing_change(self):
        points = [point("a"), point("b", CacheConfig(16, 4, 1, "LRU"), PerformanceTimingModel(2, 10, 0))]
        with self.assertRaisesRegex(ValueError, "identical timing"):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.CACHE_SIZE, points))

    def test_block_size_sweep_only_allows_block_size(self):
        valid = [point("a", CacheConfig(16, 4, 1, "LRU")), point("b", CacheConfig(16, 8, 1, "LRU"))]
        self.assertEqual(2, len(PerformanceSweepRunner().run(definition(PerformanceSweepKind.BLOCK_SIZE, valid)).point_results))
        invalid = [valid[0], point("c", CacheConfig(32, 8, 1, "LRU"))]
        with self.assertRaises(ValueError):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.BLOCK_SIZE, invalid))

    def test_associativity_sweep_only_allows_ways(self):
        valid = [point("a", CacheConfig(16, 4, 1, "LRU")), point("b", CacheConfig(16, 4, 2, "LRU"))]
        self.assertEqual(2, len(PerformanceSweepRunner().run(definition(PerformanceSweepKind.ASSOCIATIVITY, valid)).point_results))
        invalid = [valid[0], point("c", CacheConfig(32, 4, 2, "LRU"))]
        with self.assertRaises(ValueError):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.ASSOCIATIVITY, invalid))

    def test_miss_penalty_sweep_only_allows_fixed_overhead(self):
        config = CacheConfig(8, 4, 1, "LRU")
        valid = [point("a", config, PerformanceTimingModel(1, 10, 0)), point("b", config, PerformanceTimingModel(1, 20, 0))]
        PerformanceSweepRunner().run(definition(PerformanceSweepKind.MISS_PENALTY, valid))
        invalid = [valid[0], point("c", config, PerformanceTimingModel(2, 20, 0))]
        with self.assertRaisesRegex(ValueError, "only fixed miss overhead"):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.MISS_PENALTY, invalid))

    def test_hit_time_sweep_only_allows_hit_time(self):
        config = CacheConfig(8, 4, 1, "LRU")
        valid = [point("a", config, PerformanceTimingModel(1, 10, 0)), point("b", config, PerformanceTimingModel(2, 10, 0))]
        PerformanceSweepRunner().run(definition(PerformanceSweepKind.HIT_TIME, valid))
        invalid = [valid[0], point("c", config, PerformanceTimingModel(2, 20, 0))]
        with self.assertRaisesRegex(ValueError, "only hit time"):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.HIT_TIME, invalid))

    def test_custom_allows_config_and_timing_to_change(self):
        result = PerformanceSweepRunner().run(definition(PerformanceSweepKind.CUSTOM, [
            point("a"),
            point("b", CacheConfig(16, 8, 1, "FIFO"), PerformanceTimingModel(5, 50, 1)),
        ]))
        self.assertEqual(2, len(result.point_results))

    def test_best_fields_support_ties(self):
        result = PerformanceSweepRunner().run(definition(
            PerformanceSweepKind.CUSTOM,
            [point("a"), point("b")],
        ))
        self.assertEqual(("a", "b"), result.best_amat_point_ids)
        self.assertEqual(("a", "b"), result.best_hit_rate_point_ids)
        self.assertEqual(("a", "b"), result.lowest_traffic_point_ids)

    def test_random_point_is_rejected(self):
        random_point = point("random", CacheConfig(8, 4, 1, "Random"))
        with self.assertRaisesRegex(ValueError, "LRU or FIFO"):
            PerformanceSweepRunner().run(definition(PerformanceSweepKind.CUSTOM, [random_point]))

    def test_x_value_must_be_finite_and_not_boolean(self):
        for value in (math.nan, math.inf, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                point("bad", x=value)


if __name__ == "__main__":
    unittest.main()
