"""Compatibility tests for the packaged cache core and flat import facades."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig as FlatCacheConfig
from cache_line import CacheLine as FlatCacheLine
from cache_simulator import CacheSimulator as FlatCacheSimulator
from cachevis_rv.core import (
    CacheConfig,
    CacheLine,
    CacheSimulator,
    choose_victim_way,
    hit_rate,
    miss_rate,
    summarize_results,
)
from cachevis_rv.core.cache_config import CacheConfig as PackagedCacheConfig
from cachevis_rv.core.cache_line import CacheLine as PackagedCacheLine
from cachevis_rv.core.cache_simulator import CacheSimulator as PackagedCacheSimulator
from cachevis_rv.core.cache_statistics import (
    hit_rate as packaged_hit_rate,
    miss_rate as packaged_miss_rate,
    summarize_results as packaged_summarize_results,
)
from cachevis_rv.core.replacement_policy import (
    choose_victim_way as packaged_choose_victim_way,
)
from replacement_policy import choose_victim_way as flat_choose_victim_way
from statistics import (
    hit_rate as flat_hit_rate,
    miss_rate as flat_miss_rate,
    summarize_results as flat_summarize_results,
)


class CorePackageCompatibilityTest(unittest.TestCase):
    """Proves packaged and legacy imports expose the same core behavior."""

    def test_package_namespace_exports_core_symbols(self):
        self.assertIs(CacheConfig, PackagedCacheConfig)
        self.assertIs(CacheLine, PackagedCacheLine)
        self.assertIs(CacheSimulator, PackagedCacheSimulator)
        self.assertIs(choose_victim_way, packaged_choose_victim_way)
        self.assertIs(hit_rate, packaged_hit_rate)
        self.assertIs(miss_rate, packaged_miss_rate)
        self.assertIs(summarize_results, packaged_summarize_results)

    def test_flat_facades_export_same_implementation_objects(self):
        self.assertIs(FlatCacheConfig, PackagedCacheConfig)
        self.assertIs(FlatCacheLine, PackagedCacheLine)
        self.assertIs(FlatCacheSimulator, PackagedCacheSimulator)
        self.assertIs(flat_choose_victim_way, packaged_choose_victim_way)
        self.assertIs(flat_hit_rate, packaged_hit_rate)
        self.assertIs(flat_miss_rate, packaged_miss_rate)
        self.assertIs(flat_summarize_results, packaged_summarize_results)

    def test_cache_config_derived_fields_and_address_split_are_unchanged(self):
        config = PackagedCacheConfig(
            cache_size_bytes=64,
            block_size_bytes=16,
            ways=1,
        )

        self.assertEqual(config.sets, 4)
        self.assertEqual(config.offset_bits, 4)
        self.assertEqual(config.index_bits, 2)
        self.assertEqual(config.tag_bits, 26)
        self.assertEqual(
            config.split_address(0x4C),
            {"tag": 1, "index": 0, "offset": 0xC},
        )

    def test_cache_simulator_fixed_trace_matches_baseline(self):
        simulator = PackagedCacheSimulator(
            PackagedCacheConfig(
                cache_size_bytes=64,
                block_size_bytes=16,
                ways=1,
                replacement_policy="LRU",
            )
        )

        results = [simulator.access(address) for address in (0x00, 0x04, 0x40)]

        self.assertEqual([result["hit"] for result in results], [False, True, False])
        self.assertEqual([result["victim_way"] for result in results], [0, 0, 0])
        self.assertEqual(
            [result["replaced_valid"] for result in results],
            [False, False, True],
        )
        self.assertEqual(results[-1]["replaced_tag"], 0)
        self.assertEqual(
            simulator.get_statistics(),
            {
                "total_accesses": 3,
                "hits": 1,
                "misses": 2,
                "hit_rate": 1 / 3,
                "miss_rate": 2 / 3,
            },
        )
        self.assertEqual(simulator.get_cache_snapshot()[0][0]["tag"], 1)

    def test_replacement_policy_prefers_first_invalid_line(self):
        lines = [
            PackagedCacheLine(valid=True, tag=1),
            PackagedCacheLine(valid=False),
            PackagedCacheLine(valid=False),
        ]

        self.assertEqual(packaged_choose_victim_way(lines, "LRU"), 1)

    def test_replacement_policy_lru_and_fifo_are_unchanged(self):
        lru_lines = [
            PackagedCacheLine(valid=True, tag=1, last_used=5),
            PackagedCacheLine(valid=True, tag=2, last_used=2),
        ]
        fifo_lines = [
            PackagedCacheLine(valid=True, tag=1, insert_time=5),
            PackagedCacheLine(valid=True, tag=2, insert_time=2),
        ]

        self.assertEqual(packaged_choose_victim_way(lru_lines, "LRU"), 1)
        self.assertEqual(packaged_choose_victim_way(fifo_lines, "FIFO"), 1)

    def test_cache_statistics_are_unchanged(self):
        self.assertEqual(packaged_hit_rate(3, 4), 0.75)
        self.assertEqual(packaged_miss_rate(1, 4), 0.25)
        self.assertEqual(packaged_hit_rate(0, 0), 0.0)
        self.assertEqual(packaged_miss_rate(0, 0), 0.0)
        self.assertEqual(
            packaged_summarize_results(4, 3, 1),
            {
                "total_accesses": 4,
                "hits": 3,
                "misses": 1,
                "hit_rate": 0.75,
                "miss_rate": 0.25,
            },
        )


if __name__ == "__main__":
    unittest.main()
