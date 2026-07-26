"""Lower-memory transaction, byte, and final-drain accounting tests."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.write_policy import (
    MemoryAccess, MemoryAccessKind, WritePolicyComparisonSession,
    WriteTrafficAssumptions, build_traffic_delta,
)


class WritePolicyTrafficTest(unittest.TestCase):
    def test_transaction_and_byte_formulas_are_exact(self):
        delta = build_traffic_delta(
            block_size_bytes=16, store_size_bytes=4,
            block_fills=1, immediate_store_writes=1,
            bypass_writes=1, dirty_writebacks=1,
        )
        self.assertEqual(delta.block_fill_bytes, 16)
        self.assertEqual(delta.immediate_store_bytes, 4)
        self.assertEqual(delta.bypass_write_bytes, 4)
        self.assertEqual(delta.dirty_writeback_bytes, 16)
        self.assertEqual((delta.memory_read_transactions, delta.memory_read_bytes), (1, 16))
        self.assertEqual((delta.memory_write_transactions, delta.memory_write_bytes), (3, 24))
        self.assertEqual((delta.total_lower_memory_transactions, delta.total_lower_memory_bytes), (4, 40))

    def test_invalid_counts_and_store_sizes_are_rejected(self):
        with self.assertRaises(ValueError):
            build_traffic_delta(block_size_bytes=16, store_size_bytes=4, block_fills=-1)
        for value in (True, 0, -1, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                WriteTrafficAssumptions(value)

    def test_store_larger_than_block_and_cross_block_store_are_rejected_atomically(self):
        config = CacheConfig(16, 16, 1)
        with self.assertRaisesRegex(ValueError, "must not exceed"):
            WritePolicyComparisonSession(config, (), WriteTrafficAssumptions(17))
        session_access = (MemoryAccess(MemoryAccessKind.WRITE, 14),)
        with self.assertRaisesRegex(ValueError, "crosses"):
            WritePolicyComparisonSession(config, session_access, WriteTrafficAssumptions(4))

    def test_each_write_path_has_the_expected_traffic(self):
        accesses = (
            MemoryAccess(MemoryAccessKind.READ, 0),
            MemoryAccess(MemoryAccessKind.WRITE, 0),
            MemoryAccess(MemoryAccessKind.WRITE, 16),
        )
        session = WritePolicyComparisonSession(CacheConfig(16, 16, 1), accesses,
                                               WriteTrafficAssumptions(4))
        steps = session.run_all()
        lanes = {lane.lane.lane_id: lane.evidence.traffic_delta for lane in steps[1].lane_steps}
        self.assertEqual(lanes["wt_wa"].immediate_store_bytes, 4)
        self.assertEqual(lanes["wb_wa"].immediate_store_bytes, 0)
        final = {stat.lane.lane_id: stat for stat in session.statistics.lane_statistics}
        self.assertEqual(final["wb_wa"].dirty_writebacks, 1)
        self.assertEqual(final["wb_wa"].memory_write_bytes, 16)

    def test_final_drain_is_analytical_and_does_not_mutate_cache(self):
        session = WritePolicyComparisonSession(
            CacheConfig(16, 16, 1),
            (MemoryAccess(MemoryAccessKind.WRITE, 0),),
            WriteTrafficAssumptions(4),
        )
        session.run_all()
        before = session.get_cache_snapshot("wb_wa")
        stats = {stat.lane.lane_id: stat for stat in session.statistics.lane_statistics}
        after = session.get_cache_snapshot("wb_wa")
        self.assertEqual(before, after)
        self.assertEqual(stats["wb_wa"].final_dirty_bytes, 16)
        self.assertEqual(stats["wb_wa"].total_lower_memory_bytes_with_final_drain, 32)


if __name__ == "__main__":
    unittest.main()
