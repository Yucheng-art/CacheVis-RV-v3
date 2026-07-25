"""Edge case tests for cache simulator behavior."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from cache_simulator import CacheSimulator


class CacheSimulatorEdgeCaseTest(unittest.TestCase):
    """Covers replacement timing, write-through, reset, and snapshots."""

    def test_write_through_never_leaves_dirty_lines(self):
        config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)
        simulator = CacheSimulator(config)

        miss = simulator.access(0x00, "write")
        hit = simulator.access(0x04, "write")
        snapshot = simulator.get_cache_snapshot()

        self.assertFalse(miss["hit"])
        self.assertTrue(hit["hit"])
        self.assertFalse(snapshot[0][0]["dirty"])

    def test_fifo_hit_does_not_update_insert_time(self):
        config = CacheConfig(
            cache_size_bytes=64,
            block_size_bytes=16,
            ways=2,
            replacement_policy="FIFO",
        )
        simulator = CacheSimulator(config)

        simulator.access(0x00)
        first_insert_time = simulator.cache[0][0].insert_time
        simulator.access(0x20)
        simulator.access(0x00)
        hit_insert_time = simulator.cache[0][0].insert_time
        replacement = simulator.access(0x40)

        self.assertEqual(first_insert_time, hit_insert_time)
        self.assertEqual(replacement["replaced_tag"], 0)

    def test_lru_hit_updates_last_used(self):
        config = CacheConfig(
            cache_size_bytes=64,
            block_size_bytes=16,
            ways=2,
            replacement_policy="LRU",
        )
        simulator = CacheSimulator(config)

        simulator.access(0x00)
        first_last_used = simulator.cache[0][0].last_used
        simulator.access(0x20)
        simulator.access(0x00)

        self.assertGreater(simulator.cache[0][0].last_used, first_last_used)

    def test_reset_clears_stats_and_cache_lines(self):
        simulator = CacheSimulator(CacheConfig(cache_size_bytes=64, block_size_bytes=16))
        simulator.access(0x00)
        simulator.reset()

        stats = simulator.get_statistics()
        snapshot = simulator.get_cache_snapshot()

        self.assertEqual(stats["total_accesses"], 0)
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)
        self.assertTrue(all(not line["valid"] for cache_set in snapshot for line in cache_set))

    def test_snapshot_shape_is_sets_by_ways(self):
        config = CacheConfig(cache_size_bytes=128, block_size_bytes=16, ways=2)
        snapshot = CacheSimulator(config).get_cache_snapshot()

        self.assertEqual(len(snapshot), config.sets)
        self.assertTrue(all(len(cache_set) == config.ways for cache_set in snapshot))
        self.assertIn("set_index", snapshot[0][0])


if __name__ == "__main__":
    unittest.main()
