"""Per-lane and comparison invariants over every preset and partial step."""

import math
import os
import sys
import unittest
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyComparisonSession


class WritePolicyInvariantsTest(unittest.TestCase):
    def test_all_lane_formulas_hold_after_every_step(self):
        for preset in WRITE_POLICY_PRESETS:
            session = WritePolicyComparisonSession(preset.config, preset.accesses,
                                                   preset.assumptions)
            while session.has_next():
                session.step()
                for stat in session.statistics.lane_statistics:
                    self.assertEqual(stat.accesses, stat.reads + stat.writes)
                    self.assertEqual(stat.hits + stat.misses, stat.accesses)
                    self.assertEqual(stat.read_hits + stat.read_misses, stat.reads)
                    self.assertEqual(stat.write_hits + stat.write_misses, stat.writes)
                    self.assertEqual(stat.write_miss_allocations + stat.write_miss_bypasses,
                                     stat.write_misses)
                    self.assertEqual(stat.block_fills,
                                     stat.read_misses + stat.write_miss_allocations)
                    self.assertEqual(stat.dirty_writebacks, stat.dirty_evictions)
                    self.assertEqual(stat.memory_read_bytes,
                                     stat.block_fills * preset.config.block_size_bytes)
                    expected_write = (
                        stat.immediate_store_writes * preset.assumptions.store_size_bytes
                        + stat.bypass_writes * preset.assumptions.store_size_bytes
                        + stat.dirty_writebacks * preset.config.block_size_bytes
                    )
                    self.assertEqual(stat.memory_write_bytes, expected_write)
                    self.assertEqual(stat.total_lower_memory_bytes,
                                     stat.memory_read_bytes + stat.memory_write_bytes)
                    self.assertEqual(stat.final_dirty_bytes,
                                     stat.final_dirty_lines * preset.config.block_size_bytes)
                    self.assertEqual(stat.memory_write_bytes_with_final_drain,
                                     stat.memory_write_bytes + stat.final_dirty_bytes)
                    self.assertEqual(stat.total_lower_memory_bytes_with_final_drain,
                                     stat.total_lower_memory_bytes + stat.final_dirty_bytes)

    def test_comparison_partition_nonnegative_and_finite_values(self):
        for preset in WRITE_POLICY_PRESETS:
            session = WritePolicyComparisonSession(preset.config, preset.accesses,
                                                   preset.assumptions)
            session.run_all()
            stats = session.statistics
            self.assertEqual(stats.all_outcomes_agree_steps + stats.outcome_divergence_steps,
                             stats.accesses)
            for lane in stats.lane_statistics:
                for field in fields(lane):
                    value = getattr(lane, field.name)
                    if isinstance(value, int):
                        self.assertGreaterEqual(value, 0)
                        self.assertTrue(math.isfinite(value))

    def test_empty_trace_statistics_are_zero_and_partitioned(self):
        preset = WRITE_POLICY_PRESETS[0]
        session = WritePolicyComparisonSession(preset.config, (), preset.assumptions)
        stats = session.statistics
        self.assertEqual(stats.accesses, 0)
        self.assertEqual(stats.all_outcomes_agree_steps, 0)
        self.assertEqual(stats.outcome_divergence_steps, 0)
        self.assertTrue(all(lane.accesses == 0 for lane in stats.lane_statistics))

    def test_dirty_and_cache_state_divergence_definitions_are_distinct(self):
        source_path = Path(__file__).resolve().parents[1] / "src" / "cachevis_rv" / "labs" / "write_policy" / "session.py"
        source = source_path.read_text(encoding="utf-8")
        self.assertIn("line.valid and line.dirty", source)
        self.assertIn("step.after_cache_snapshot", source)


if __name__ == "__main__":
    unittest.main()
