"""Strict access-result evidence contract for core write policies."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheLine, CacheSimulator


EXPECTED_FIELDS = {
    "access_id", "address", "operation", "tag", "index", "offset", "hit",
    "victim_way", "replaced_valid", "replaced_tag", "allocated", "bypassed",
    "hit_way", "fill_way", "evicted_way", "victim_tag", "victim_dirty",
    "line_dirty_before", "line_dirty_after", "total_accesses", "hits", "misses",
    "hit_rate",
}


def simulator(write_policy="write-through", write_allocate=True):
    return CacheSimulator(CacheConfig(
        cache_size_bytes=16, block_size_bytes=16, ways=1,
        write_policy=write_policy, write_allocate=write_allocate,
    ))


class CoreWritePolicyAccessResultTest(unittest.TestCase):
    def test_result_has_exact_backward_compatible_and_new_field_set(self):
        self.assertEqual(set(simulator().access(0)), EXPECTED_FIELDS)

    def test_hit_evidence_separates_legacy_access_way(self):
        cache = simulator()
        cache.access(0)
        result = cache.access(0)
        self.assertEqual(result["victim_way"], 0)  # legacy accessed-way field
        self.assertEqual(result["hit_way"], 0)
        self.assertIsNone(result["fill_way"])
        self.assertIsNone(result["evicted_way"])
        self.assertIsNone(result["victim_tag"])
        self.assertFalse(result["victim_dirty"])

    def test_invalid_fill_evidence_has_fill_but_no_eviction(self):
        result = simulator().access(0)
        self.assertTrue(result["allocated"])
        self.assertFalse(result["bypassed"])
        self.assertIsNone(result["hit_way"])
        self.assertEqual(result["fill_way"], 0)
        self.assertIsNone(result["evicted_way"])
        self.assertFalse(result["replaced_valid"])
        self.assertIsNone(result["victim_tag"])
        self.assertFalse(result["victim_dirty"])

    def test_eviction_evidence_comes_from_replaced_line(self):
        cache = simulator("write-back")
        cache.access(0, "write")
        result = cache.access(16, "write")
        self.assertEqual(result["fill_way"], 0)
        self.assertEqual(result["evicted_way"], 0)
        self.assertEqual(result["victim_tag"], 0)
        self.assertTrue(result["victim_dirty"])
        self.assertEqual(result["replaced_tag"], 0)

    def test_bypass_evidence_has_no_cache_way_or_mutable_line(self):
        result = simulator("write-back", False).access(0, "write")
        self.assertFalse(result["allocated"])
        self.assertTrue(result["bypassed"])
        for field in ("victim_way", "hit_way", "fill_way", "evicted_way", "victim_tag"):
            self.assertIsNone(result[field])
        self.assertFalse(result["victim_dirty"])
        self.assertNotIn(CacheLine, (type(value) for value in result.values()))

    def test_allocated_and_bypassed_are_mutually_exclusive(self):
        cases = (
            simulator().access(0, "read"),
            simulator().access(0, "write"),
            simulator(write_allocate=False).access(0, "write"),
        )
        for result in cases:
            self.assertFalse(result["allocated"] and result["bypassed"])


if __name__ == "__main__":
    unittest.main()
