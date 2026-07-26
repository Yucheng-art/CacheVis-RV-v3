import math
import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import (
    ANALYTICAL_L1_L2_MODEL,
    PERFORMANCE_PRESETS,
    PERFORMANCE_SWEEP_PRESETS,
    PerformanceSweepRunner,
    TwoLevelPerformanceAnalyzer,
)


class PerformancePresetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {
            sweep.sweep_id: PerformanceSweepRunner().run(sweep)
            for sweep in PERFORMANCE_SWEEP_PRESETS
        }

    def metrics(self, sweep_id):
        return {
            item.point_id: item.run_result.metrics
            for item in self.results[sweep_id].point_results
        }

    def test_seven_preset_ids_are_unique_and_data_is_frozen(self):
        self.assertEqual(7, len(PERFORMANCE_PRESETS))
        self.assertEqual(7, len({preset.preset_id for preset in PERFORMANCE_PRESETS}))
        with self.assertRaises(FrozenInstanceError):
            PERFORMANCE_PRESETS[0].title = "changed"

    def test_capacity_knee_exact_results_and_ties(self):
        metrics = self.metrics("capacity_knee")
        self.assertEqual((0, 16), (metrics["cache_8"].hits, metrics["cache_8"].misses))
        for point_id in ("cache_16", "cache_32"):
            self.assertEqual((12, 4), (metrics[point_id].hits, metrics[point_id].misses))
        result = self.results["capacity_knee"]
        self.assertEqual(("cache_16", "cache_32"), result.best_amat_point_ids)
        self.assertEqual(metrics["cache_16"].amat_cycles, metrics["cache_32"].amat_cycles)

    def test_sequential_block_benefit_exact_results(self):
        metrics = self.metrics("sequential_block_benefit")
        expected = {
            "block_4": (0, 8, 22.0, 23.0),
            "block_8": (4, 4, 24.0, 13.0),
            "block_16": (6, 2, 28.0, 8.0),
        }
        for point_id, values in expected.items():
            item = metrics[point_id]
            self.assertEqual(values, (item.hits, item.misses, item.effective_miss_penalty_cycles, item.amat_cycles))

    def test_stride_block_cost_exact_results(self):
        metrics = self.metrics("stride_block_cost")
        for point_id in ("block_4", "block_8", "block_16"):
            self.assertEqual((0, 4), (metrics[point_id].hits, metrics[point_id].misses))
        self.assertEqual((23.0, 25.0, 29.0), tuple(metrics[p].amat_cycles for p in ("block_4", "block_8", "block_16")))

    def test_associativity_conflict_relief_exact_results(self):
        metrics = self.metrics("associativity_conflict_relief")
        self.assertEqual((0, 6), (metrics["ways_1"].hits, metrics["ways_1"].misses))
        self.assertEqual((4, 2), (metrics["ways_2"].hits, metrics["ways_2"].misses))
        self.assertEqual((4, 2), (metrics["ways_4"].hits, metrics["ways_4"].misses))
        self.assertEqual(("ways_2", "ways_4"), self.results["associativity_conflict_relief"].best_hit_rate_point_ids)

    def test_miss_penalty_sensitivity_exact_results(self):
        metrics = self.metrics("miss_penalty_sensitivity")
        self.assertEqual((6.0, 26.0, 51.0), tuple(metrics[p].amat_cycles for p in ("penalty_10", "penalty_50", "penalty_100")))
        for item in metrics.values():
            self.assertEqual((2, 2, 0.5), (item.hits, item.misses, item.miss_rate))

    def test_hit_rate_is_not_amat_counterexample(self):
        metrics = self.metrics("hit_rate_is_not_amat")
        fast = metrics["fast_small"]
        slow = metrics["slow_large"]
        self.assertEqual((0, 4, 1.0, 11.0), (fast.hits, fast.misses, fast.miss_rate, fast.amat_cycles))
        self.assertEqual((2, 2, 0.5, 13.0), (slow.hits, slow.misses, slow.miss_rate, slow.amat_cycles))
        self.assertGreater(slow.hit_rate, fast.hit_rate)
        self.assertGreater(slow.amat_cycles, fast.amat_cycles)

    def test_analytical_l1_l2_exact_result(self):
        result = TwoLevelPerformanceAnalyzer.analyze(ANALYTICAL_L1_L2_MODEL)
        self.assertTrue(math.isclose(0.9, result.l1_hit_probability))
        self.assertTrue(math.isclose(0.075, result.l2_hit_probability_global))
        self.assertTrue(math.isclose(0.025, result.memory_access_probability))
        self.assertTrue(math.isclose(3.8, result.amat_cycles))


if __name__ == "__main__":
    unittest.main()
