"""M5.1 contract checks against the formal M5.0 cache core."""

import inspect
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheSimulator
from cachevis_rv.labs.write_policy import WRITE_POLICY_LANES, MemoryAccess, MemoryAccessKind


class WritePolicyAuditContractTest(unittest.TestCase):
    def test_four_lanes_use_formal_core_configuration_values(self):
        self.assertEqual(
            tuple((lane.write_policy, lane.write_allocate) for lane in WRITE_POLICY_LANES),
            (("write-through", True), ("write-through", False),
             ("write-back", True), ("write-back", False)),
        )
        for lane in WRITE_POLICY_LANES:
            CacheConfig(write_policy=lane.write_policy, write_allocate=lane.write_allocate)

    def test_core_access_is_the_read_write_api_and_eviction_uses_evicted_way(self):
        self.assertEqual(tuple(inspect.signature(CacheSimulator.access).parameters),
                         ("self", "address", "operation"))
        cache = CacheSimulator(CacheConfig(16, 16, 1, "LRU", "write-back"))
        cache.access(0, "write")
        result = cache.access(16, "write")
        self.assertEqual(result["evicted_way"], 0)
        self.assertTrue(result["victim_dirty"])

    def test_core_semantics_cover_clean_dirty_bypass_and_read_eviction(self):
        wt = CacheSimulator(CacheConfig(16, 16, 1, write_policy="write-through"))
        wb = CacheSimulator(CacheConfig(16, 16, 1, write_policy="write-back"))
        nwa = CacheSimulator(CacheConfig(16, 16, 1, write_policy="write-back", write_allocate=False))
        wt.access(0, "write")
        wb.access(0, "write")
        before = nwa.get_cache_snapshot()
        bypass = nwa.access(0, "write")
        read_eviction = wb.access(16, "read")
        self.assertFalse(wt.get_cache_snapshot()[0][0]["dirty"])
        self.assertTrue(bypass["bypassed"])
        self.assertEqual(nwa.get_cache_snapshot(), before)
        self.assertTrue(read_eviction["victim_dirty"])

    def test_access_model_is_pure_input_data(self):
        self.assertEqual(MemoryAccess(MemoryAccessKind.READ, 4).address, 4)


if __name__ == "__main__":
    unittest.main()
