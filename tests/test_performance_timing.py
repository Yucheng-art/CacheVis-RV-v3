import math
import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.performance import PerformanceTimingModel


class PerformanceTimingModelTest(unittest.TestCase):
    def test_valid_model_is_frozen_and_normalized(self):
        model = PerformanceTimingModel(1, 20, 0.5)
        self.assertEqual((1.0, 20.0, 0.5), (
            model.hit_time_cycles,
            model.fixed_miss_overhead_cycles,
            model.transfer_cycles_per_byte,
        ))
        with self.assertRaises(FrozenInstanceError):
            model.hit_time_cycles = 2

    def test_effective_penalty_formula(self):
        self.assertEqual(28.0, PerformanceTimingModel(1, 20, 0.5).effective_miss_penalty(16))

    def test_hit_time_must_be_positive(self):
        for value in (0, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PerformanceTimingModel(value, 0, 0)

    def test_miss_overhead_must_be_non_negative(self):
        with self.assertRaises(ValueError):
            PerformanceTimingModel(1, -0.1, 0)

    def test_transfer_cost_must_be_non_negative(self):
        with self.assertRaises(ValueError):
            PerformanceTimingModel(1, 0, -0.1)

    def test_nan_and_infinity_are_rejected(self):
        for value in (math.nan, math.inf, -math.inf):
            for field in range(3):
                values = [1, 0, 0]
                values[field] = value
                with self.subTest(value=value, field=field), self.assertRaises(ValueError):
                    PerformanceTimingModel(*values)

    def test_boolean_and_non_numeric_inputs_are_rejected(self):
        with self.assertRaises(TypeError):
            PerformanceTimingModel(True, 0, 0)
        with self.assertRaises(TypeError):
            PerformanceTimingModel(1, "20", 0)

    def test_block_size_must_be_positive_integer(self):
        model = PerformanceTimingModel(1, 20, 0.5)
        for value in (0, -1, 4.0, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                model.effective_miss_penalty(value)


if __name__ == "__main__":
    unittest.main()
