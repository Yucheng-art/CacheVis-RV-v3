import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.performance import (
    CAPACITY_KNEE_SWEEP,
    HIT_RATE_IS_NOT_AMAT_SWEEP,
    PerformanceRunSpec,
    PerformanceSweepDefinition,
    PerformanceSweepKind,
    PerformanceSweepRunner,
    PerformanceTimingModel,
    build_comparison_view_model,
)


class PerformanceComparisonViewModelTest(unittest.TestCase):
    def test_hit_rate_not_amat_creates_formal_tradeoff_pair(self):
        result = PerformanceSweepRunner().run(HIT_RATE_IS_NOT_AMAT_SWEEP)
        view = build_comparison_view_model(result)
        self.assertTrue(view.hit_rate_amat_ranking_disagrees)
        self.assertEqual(1, len(view.tradeoff_pairs))
        pair = view.tradeoff_pairs[0]
        self.assertEqual("slow_large", pair.higher_hit_rate_point_id)
        self.assertEqual("fast_small", pair.lower_hit_rate_point_id)
        self.assertEqual((0.5, 0.0), (pair.higher_hit_rate, pair.lower_hit_rate))
        self.assertEqual((13.0, 11.0), (pair.higher_amat, pair.lower_amat))
        self.assertTrue(pair.higher_hit_rate_has_worse_amat)

    def test_fastest_uses_total_cycles_and_supports_tie(self):
        capacity = build_comparison_view_model(PerformanceSweepRunner().run(CAPACITY_KNEE_SWEEP))
        self.assertEqual(("cache_16", "cache_32"), capacity.fastest_point_ids)
        self.assertEqual(("cache_8",), capacity.slowest_point_ids)
        tradeoff = build_comparison_view_model(PerformanceSweepRunner().run(HIT_RATE_IS_NOT_AMAT_SWEEP))
        self.assertEqual(("fast_small",), tradeoff.fastest_point_ids)
        self.assertEqual(("slow_large",), tradeoff.slowest_point_ids)

    def test_speedup_bounds_and_baseline_are_mapped(self):
        view = build_comparison_view_model(PerformanceSweepRunner().run(CAPACITY_KNEE_SWEEP))
        self.assertEqual("cache_8", view.baseline_point_id)
        self.assertEqual(1.0, view.baseline_speedup)
        self.assertGreater(view.maximum_speedup, view.minimum_speedup)

    def test_empty_trace_does_not_create_false_rankings(self):
        config = CacheConfig(8, 4, 1, "LRU")
        timing = PerformanceTimingModel(1, 10, 0)
        definition = PerformanceSweepDefinition(
            "empty", "Empty", "Empty trace.", PerformanceSweepKind.CUSTOM, (),
            (PerformanceRunSpec("a", "A", 1, config, timing), PerformanceRunSpec("b", "B", 2, config, timing)),
            "a", "Empty.",
        )
        view = build_comparison_view_model(PerformanceSweepRunner().run(definition))
        self.assertEqual((), view.fastest_point_ids)
        self.assertEqual((), view.slowest_point_ids)
        self.assertEqual((), view.tradeoff_pairs)
        self.assertIsNone(view.maximum_speedup)
        self.assertIsNone(view.minimum_speedup)
        self.assertTrue(view.all_total_cycles_equal)

    def test_teaching_insight_does_not_claim_universal_best(self):
        view = build_comparison_view_model(PerformanceSweepRunner().run(CAPACITY_KNEE_SWEEP))
        self.assertIn("only this completed trace", view.teaching_insight)
        self.assertNotIn("universally best", view.teaching_insight.lower())


if __name__ == "__main__":
    unittest.main()
