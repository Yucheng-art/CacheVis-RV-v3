"""Tests for a 1-way direct mapped cache."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from cache_simulator import CacheSimulator


class DirectMappedCacheTest(unittest.TestCase):
    """Covers basic hit and conflict miss behavior."""

    def test_basic_hit_and_miss(self):
        config = CacheConfig(
            cache_size_bytes=64,
            block_size_bytes=16,
            ways=1,
            replacement_policy="LRU",
        )
        simulator = CacheSimulator(config)

        first = simulator.access(0x00)
        second = simulator.access(0x04)
        third = simulator.access(0x40)

        self.assertFalse(first["hit"])
        self.assertTrue(second["hit"])
        self.assertFalse(third["hit"])
        self.assertTrue(third["replaced_valid"])
        self.assertEqual(simulator.get_statistics()["hits"], 1)
        self.assertEqual(simulator.get_statistics()["misses"], 2)


if __name__ == "__main__":
    unittest.main()
