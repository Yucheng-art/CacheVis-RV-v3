import math
import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import (
    TwoLevelPerformanceAnalyzer,
    TwoLevelTimingModel,
)


class TwoLevelPerformanceTest(unittest.TestCase):
    def analyze(self, l1_miss=0.10, l2_miss=0.25):
        return TwoLevelPerformanceAnalyzer.analyze(
            TwoLevelTimingModel(1, l1_miss, 8, l2_miss, 80)
        )

    def test_formal_example_is_3_point_8_cycles(self):
        result = self.analyze()
        self.assertTrue(math.isclose(0.90, result.l1_hit_probability))
        self.assertTrue(math.isclose(0.075, result.l2_hit_probability_global))
        self.assertTrue(math.isclose(0.025, result.memory_access_probability))
        self.assertTrue(math.isclose(0.025, result.l2_global_miss_rate))
        self.assertEqual((1.0, 0.8, 2.0, 3.8), (
            result.l1_contribution_cycles,
            result.l2_contribution_cycles,
            result.memory_contribution_cycles,
            result.amat_cycles,
        ))

    def test_probability_partition_and_contribution_sum(self):
        result = self.analyze()
        self.assertTrue(result.probability_partition_ok)
        self.assertTrue(result.contribution_sum_ok)
        self.assertTrue(math.isclose(1.0, result.l1_hit_probability + result.l2_hit_probability_global + result.memory_access_probability))
        self.assertTrue(math.isclose(result.amat_cycles, result.l1_contribution_cycles + result.l2_contribution_cycles + result.memory_contribution_cycles))

    def test_l1_miss_zero_boundary(self):
        result = self.analyze(l1_miss=0)
        self.assertEqual((1.0, 0.0, 0.0, 1.0), (
            result.l1_hit_probability,
            result.l2_hit_probability_global,
            result.memory_access_probability,
            result.amat_cycles,
        ))

    def test_l1_miss_one_boundary(self):
        result = self.analyze(l1_miss=1)
        self.assertEqual(0.0, result.l1_hit_probability)
        self.assertEqual(0.75, result.l2_hit_probability_global)
        self.assertEqual(0.25, result.memory_access_probability)
        self.assertEqual(29.0, result.amat_cycles)

    def test_l2_local_miss_zero_boundary(self):
        result = self.analyze(l2_miss=0)
        self.assertEqual(0.10, result.l2_hit_probability_global)
        self.assertEqual(0.0, result.memory_access_probability)
        self.assertEqual(1.8, result.amat_cycles)

    def test_l2_local_miss_one_boundary(self):
        result = self.analyze(l2_miss=1)
        self.assertEqual(0.0, result.l2_hit_probability_global)
        self.assertEqual(0.10, result.memory_access_probability)
        self.assertEqual(9.8, result.amat_cycles)

    def test_invalid_rates_are_rejected(self):
        for l1, l2 in ((-0.1, 0), (1.1, 0), (0, -0.1), (0, 1.1)):
            with self.subTest(l1=l1, l2=l2), self.assertRaises(ValueError):
                TwoLevelTimingModel(1, l1, 8, l2, 80)

    def test_nan_and_infinity_are_rejected(self):
        valid = [1, 0.1, 8, 0.25, 80]
        for index in range(5):
            for bad in (math.nan, math.inf):
                values = list(valid)
                values[index] = bad
                with self.subTest(index=index, bad=bad), self.assertRaises(ValueError):
                    TwoLevelTimingModel(*values)

    def test_hit_times_are_positive_and_memory_penalty_non_negative(self):
        with self.assertRaises(ValueError):
            TwoLevelTimingModel(0, 0.1, 8, 0.2, 80)
        with self.assertRaises(ValueError):
            TwoLevelTimingModel(1, 0.1, 0, 0.2, 80)
        with self.assertRaises(ValueError):
            TwoLevelTimingModel(1, 0.1, 8, 0.2, -1)

    def test_models_and_results_are_frozen(self):
        model = TwoLevelTimingModel(1, 0.1, 8, 0.25, 80)
        result = TwoLevelPerformanceAnalyzer.analyze(model)
        with self.assertRaises(FrozenInstanceError):
            model.l1_miss_rate = 0.5
        with self.assertRaises(FrozenInstanceError):
            result.amat_cycles = 0

    def test_analyzer_requires_formal_model(self):
        with self.assertRaises(TypeError):
            TwoLevelPerformanceAnalyzer.analyze(object())


if __name__ == "__main__":
    unittest.main()
