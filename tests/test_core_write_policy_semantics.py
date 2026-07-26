"""Read, write, allocation, and bypass semantics in the formal simulator."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheSimulator


def simulator(write_policy="write-through", write_allocate=True):
    return CacheSimulator(
        CacheConfig(
            cache_size_bytes=16,
            block_size_bytes=16,
            ways=1,
            replacement_policy="LRU",
            write_policy=write_policy,
            write_allocate=write_allocate,
        )
    )


class CoreWritePolicySemanticsTest(unittest.TestCase):
    def test_write_through_allocate_miss_and_hit_stay_clean(self):
        cache = simulator()
        miss = cache.access(0, "write")
        hit = cache.access(0, "write")
        self.assertFalse(miss["hit"])
        self.assertTrue(miss["allocated"])
        self.assertFalse(miss["bypassed"])
        self.assertTrue(hit["hit"])
        self.assertFalse(cache.get_cache_snapshot()[0][0]["dirty"])

    def test_write_back_allocate_miss_and_hit_are_dirty(self):
        cache = simulator("write-back")
        miss = cache.access(0, "write")
        hit = cache.access(0, "write")
        self.assertTrue(miss["allocated"])
        self.assertIs(miss["line_dirty_after"], True)
        self.assertTrue(hit["hit"])
        self.assertIs(hit["line_dirty_before"], True)
        self.assertIs(hit["line_dirty_after"], True)

    def test_no_write_allocate_misses_bypass_and_preserve_complete_snapshot(self):
        for policy in ("write-through", "write-back"):
            with self.subTest(policy=policy):
                cache = simulator(policy, False)
                before = cache.get_cache_snapshot()
                result = cache.access(0, "write")
                self.assertFalse(result["hit"])
                self.assertFalse(result["allocated"])
                self.assertTrue(result["bypassed"])
                self.assertEqual(cache.get_cache_snapshot(), before)

    def test_read_miss_allocates_clean_regardless_of_allocation_policy(self):
        for policy in ("write-through", "write-back"):
            for allocate in (True, False):
                with self.subTest(policy=policy, allocate=allocate):
                    cache = simulator(policy, allocate)
                    result = cache.access(0, "read")
                    self.assertTrue(result["allocated"])
                    self.assertFalse(result["bypassed"])
                    self.assertFalse(cache.get_cache_snapshot()[0][0]["dirty"])

    def test_read_hit_preserves_dirty_and_resident_nwa_write_hit_uses_policy(self):
        cache = simulator("write-back", False)
        cache.access(0, "read")
        write = cache.access(0, "write")
        read = cache.access(0, "read")
        self.assertTrue(write["hit"])
        self.assertFalse(write["allocated"])
        self.assertFalse(write["bypassed"])
        self.assertIs(write["line_dirty_after"], True)
        self.assertIs(read["line_dirty_before"], True)
        self.assertIs(read["line_dirty_after"], True)

    def test_bypass_counts_as_miss_and_reset_restores_cold_cache(self):
        cache = simulator("write-back", False)
        cache.access(0, "write")
        self.assertEqual(cache.get_statistics(), {
            "total_accesses": 1, "hits": 0, "misses": 1,
            "hit_rate": 0.0, "miss_rate": 1.0,
        })
        cache.reset()
        self.assertEqual(cache.total_accesses, 0)
        self.assertTrue(all(
            not line["valid"] and not line["dirty"]
            for cache_set in cache.get_cache_snapshot() for line in cache_set
        ))


if __name__ == "__main__":
    unittest.main()
