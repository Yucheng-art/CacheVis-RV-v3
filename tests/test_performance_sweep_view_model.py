import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import (
    ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP,
    CAPACITY_KNEE_SWEEP,
    MISS_PENALTY_SENSITIVITY_SWEEP,
    SEQUENTIAL_BLOCK_BENEFIT_SWEEP,
    STRIDE_BLOCK_COST_SWEEP,
    PerformanceSweepRunner,
    build_sweep_point_view_models,
    build_sweep_summary_view_model,
)


class PerformanceSweepViewModelTest(unittest.TestCase):
    def result(self, definition):
        return PerformanceSweepRunner().run(definition)

    def test_point_order_baseline_and_selected_are_stable(self):
        result = self.result(CAPACITY_KNEE_SWEEP)
        points = build_sweep_point_view_models(result, "cache_32")
        self.assertEqual(tuple(p.point_id for p in result.point_results), tuple(p.point_id for p in points))
        self.assertTrue(points[0].is_baseline)
        self.assertFalse(points[0].is_selected)
        self.assertTrue(points[2].is_selected)

    def test_all_best_ties_are_marked(self):
        result = self.result(CAPACITY_KNEE_SWEEP)
        points = build_sweep_point_view_models(result, result.baseline_point_id)
        self.assertEqual(("cache_16", "cache_32"), tuple(p.point_id for p in points if p.is_best_amat))
        self.assertEqual(("cache_16", "cache_32"), tuple(p.point_id for p in points if p.is_best_hit_rate))
        self.assertEqual(("cache_16", "cache_32"), tuple(p.point_id for p in points if p.is_lowest_traffic))

    def test_speedup_and_deltas_map_exactly(self):
        result = self.result(CAPACITY_KNEE_SWEEP)
        points = build_sweep_point_view_models(result, result.baseline_point_id)
        for domain, view in zip(result.point_results, points):
            self.assertEqual(domain.speedup_vs_baseline, view.speedup_vs_baseline)
            self.assertEqual(domain.amat_delta_vs_baseline, view.amat_delta_vs_baseline)
            self.assertEqual(domain.total_cycles_delta_vs_baseline, view.total_cycles_delta_vs_baseline)

    def test_capacity_summary_expresses_amat_tie_as_actual_observation(self):
        summary = build_sweep_summary_view_model(self.result(CAPACITY_KNEE_SWEEP))
        self.assertTrue(summary.best_amat_is_tie)
        self.assertEqual(("16 B cache", "32 B cache"), summary.best_amat_labels)
        self.assertTrue(any("AMAT tie" in text and "16 B cache" in text and "32 B cache" in text for text in summary.actual_observations))

    def test_sequential_summary_observes_miss_reduction(self):
        summary = build_sweep_summary_view_model(self.result(SEQUENTIAL_BLOCK_BENEFIT_SWEEP))
        self.assertTrue(any("misses range from 2 to 8" in text for text in summary.actual_observations))

    def test_stride_summary_observes_equal_misses_and_penalty_range(self):
        summary = build_sweep_summary_view_model(self.result(STRIDE_BLOCK_COST_SWEEP))
        self.assertTrue(any("All points produced 4 misses" in text for text in summary.actual_observations))
        self.assertTrue(any("penalty ranges from 22.0 to 28.0" in text for text in summary.actual_observations))

    def test_associativity_summary_preserves_two_way_four_way_tie(self):
        summary = build_sweep_summary_view_model(self.result(ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP))
        self.assertEqual(("ways_2", "ways_4"), summary.best_amat_point_ids)
        self.assertTrue(summary.best_amat_is_tie)

    def test_miss_penalty_summary_separates_expected_and_actual(self):
        summary = build_sweep_summary_view_model(self.result(MISS_PENALTY_SENSITIVITY_SWEEP))
        self.assertEqual(MISS_PENALTY_SENSITIVITY_SWEEP.expected_teaching_conclusion, summary.expected_teaching_conclusion)
        self.assertNotIn(summary.expected_teaching_conclusion, summary.actual_observations)
        self.assertTrue(any("All points produced 2 misses" in text for text in summary.actual_observations))
        self.assertTrue(any("AMAT ranges from 6.0 to 51.0" in text for text in summary.actual_observations))

    def test_unknown_selected_point_is_rejected(self):
        with self.assertRaises(ValueError):
            build_sweep_point_view_models(self.result(CAPACITY_KNEE_SWEEP), "missing")


if __name__ == "__main__":
    unittest.main()
