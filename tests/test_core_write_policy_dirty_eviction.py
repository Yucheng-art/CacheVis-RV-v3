"""Dirty-victim evidence across reads, writes, and associativities."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheSimulator


class CoreWritePolicyDirtyEvictionTest(unittest.TestCase):
    def make_cache(self, ways=1):
        return CacheSimulator(CacheConfig(
            cache_size_bytes=16 * ways,
            block_size_bytes=16,
            ways=ways,
            replacement_policy="LRU",
            write_policy="write-back",
        ))

    def test_write_miss_evicts_dirty_direct_mapped_victim(self):
        cache = self.make_cache()
        cache.access(0, "write")
        result = cache.access(16, "write")
        self.assertEqual((result["evicted_way"], result["victim_tag"]), (0, 0))
        self.assertTrue(result["victim_dirty"])
        line = cache.get_cache_snapshot()[0][0]
        self.assertEqual(line["tag"], 1)
        self.assertTrue(line["dirty"])

    def test_read_miss_evicts_dirty_victim_and_fills_clean(self):
        cache = self.make_cache()
        cache.access(0, "write")
        result = cache.access(16, "read")
        self.assertEqual(result["victim_tag"], 0)
        self.assertTrue(result["victim_dirty"])
        self.assertFalse(result["line_dirty_after"])
        self.assertFalse(cache.get_cache_snapshot()[0][0]["dirty"])

    def test_clean_victim_is_reported_as_clean(self):
        cache = self.make_cache()
        cache.access(0, "read")
        result = cache.access(16, "read")
        self.assertTrue(result["replaced_valid"])
        self.assertFalse(result["victim_dirty"])

    def test_lru_set_associative_dirty_victim_is_preserved_before_overwrite(self):
        cache = self.make_cache(ways=2)
        cache.access(0, "write")
        cache.access(16, "read")
        cache.access(16, "read")
        result = cache.access(32, "read")
        self.assertEqual(result["evicted_way"], 0)
        self.assertEqual(result["victim_tag"], 0)
        self.assertTrue(result["victim_dirty"])

    def test_invalid_fill_never_claims_dirty_victim(self):
        result = self.make_cache(ways=2).access(0, "write")
        self.assertFalse(result["replaced_valid"])
        self.assertIsNone(result["evicted_way"])
        self.assertIsNone(result["victim_tag"])
        self.assertFalse(result["victim_dirty"])


if __name__ == "__main__":
    unittest.main()
