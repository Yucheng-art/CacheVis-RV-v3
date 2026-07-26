import math
import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.performance import (
    PerformanceCacheLineSnapshot,
    PerformanceRunner,
    PerformanceTimingModel,
)


class PerformanceRunnerTest(unittest.TestCase):
    def setUp(self):
        self.runner = PerformanceRunner()
        self.config = CacheConfig(8, 4, 1, "LRU")
        self.timing = PerformanceTimingModel(2, 10, 0.5)

    def test_official_hits_and_misses_feed_metrics(self):
        metrics = self.runner.run(self.config, (0, 4, 0, 4), self.timing).metrics
        self.assertEqual((4, 2, 2), (metrics.accesses, metrics.hits, metrics.misses))
        self.assertEqual((0.5, 0.5), (metrics.hit_rate, metrics.miss_rate))

    def test_cycle_and_amat_formulas(self):
        metrics = self.runner.run(self.config, (0, 4, 0, 4), self.timing).metrics
        self.assertEqual(12.0, metrics.effective_miss_penalty_cycles)
        self.assertEqual(8.0, metrics.total_lookup_cycles)
        self.assertEqual(24.0, metrics.total_miss_penalty_cycles)
        self.assertEqual(32.0, metrics.total_cycles)
        self.assertEqual(8.0, metrics.amat_cycles)
        self.assertTrue(math.isclose(2 + 0.5 * 12, metrics.amat_cycles))

    def test_traffic_and_stall_formulas(self):
        metrics = self.runner.run(self.config, (0, 4, 0, 4), self.timing).metrics
        self.assertEqual(metrics.misses, metrics.line_fills)
        self.assertEqual(8, metrics.bytes_fetched)
        self.assertEqual(2.0, metrics.bytes_fetched_per_access)
        self.assertEqual(0.75, metrics.miss_stall_fraction)

    def test_empty_trace_has_explicit_none_averages(self):
        metrics = self.runner.run(self.config, (), self.timing).metrics
        self.assertEqual((0, 0, 0), (metrics.accesses, metrics.hits, metrics.misses))
        self.assertEqual((0.0, 0.0, 0.0), (metrics.hit_rate, metrics.miss_rate, metrics.total_cycles))
        self.assertIsNone(metrics.amat_cycles)
        self.assertIsNone(metrics.bytes_fetched_per_access)
        self.assertIsNone(metrics.miss_stall_fraction)

    def test_negative_address_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            self.runner.run(self.config, (0, -1), self.timing)

    def test_address_width_upper_bound_is_rejected(self):
        config = CacheConfig(8, 4, 1, "LRU", address_bits=4)
        with self.assertRaisesRegex(ValueError, "address width"):
            self.runner.run(config, (16,), self.timing)

    def test_non_integer_and_boolean_addresses_are_rejected(self):
        for address in (1.5, "1", True):
            with self.subTest(address=address), self.assertRaises(TypeError):
                self.runner.run(self.config, (address,), self.timing)

    def test_inputs_are_not_modified_and_result_has_stable_copies(self):
        addresses = [0, 4, 0]
        original = list(addresses)
        result = self.runner.run(self.config, addresses, self.timing)
        self.assertEqual(original, addresses)
        self.assertEqual(tuple(original), result.addresses)
        self.assertEqual(self.config, result.config)
        self.assertIsNot(self.config, result.config)

    def test_each_run_is_an_independent_cold_start(self):
        first = self.runner.run(self.config, (0,), self.timing)
        second = self.runner.run(self.config, (0,), self.timing)
        self.assertEqual((0, 1), (first.metrics.hits, first.metrics.misses))
        self.assertEqual(first.metrics, second.metrics)
        self.assertEqual(first.final_cache_snapshot, second.final_cache_snapshot)

    def test_lru_and_fifo_are_supported(self):
        for policy in ("LRU", "FIFO"):
            config = CacheConfig(8, 4, 2, policy)
            with self.subTest(policy=policy):
                result = self.runner.run(config, (0, 4, 0, 8), self.timing)
                self.assertEqual(4, result.metrics.accesses)

    def test_random_is_rejected_with_formal_message(self):
        config = CacheConfig(8, 4, 2, "Random")
        with self.assertRaisesRegex(ValueError, "Random performance ranking belongs to Policy Lab"):
            self.runner.run(config, (0, 4), self.timing)

    def test_snapshot_is_detached_immutable_value_data(self):
        result = self.runner.run(self.config, (0,), self.timing)
        line = result.final_cache_snapshot[0][0]
        self.assertIsInstance(result.final_cache_snapshot, tuple)
        self.assertIsInstance(result.final_cache_snapshot[0], tuple)
        self.assertIsInstance(line, PerformanceCacheLineSnapshot)
        with self.assertRaises(FrozenInstanceError):
            line.tag = 99
        self.assertNotIn("CacheLine", type(line).__module__)

    def test_generator_addresses_are_copied(self):
        result = self.runner.run(self.config, (value for value in (0, 4)), self.timing)
        self.assertEqual((0, 4), result.addresses)

    def test_bad_config_timing_and_addresses_types_are_rejected(self):
        with self.assertRaises(TypeError):
            self.runner.run(object(), (), self.timing)
        with self.assertRaises(TypeError):
            self.runner.run(self.config, (), object())
        with self.assertRaises(TypeError):
            self.runner.run(self.config, "0 4", self.timing)


if __name__ == "__main__":
    unittest.main()
