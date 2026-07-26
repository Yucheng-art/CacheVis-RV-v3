"""Decision evidence and metadata cross-check tests."""

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig, CacheSimulator
from cachevis_rv.labs.write_policy import (
    MemoryAccess, MemoryAccessKind, WRITE_POLICY_LANES, WriteDecisionKind,
    WritePolicyComparisonSession, WritePolicyExplainer, WriteTrafficAssumptions,
    snapshot_cache,
)


def session(trace):
    return WritePolicyComparisonSession(CacheConfig(16, 16, 1), trace,
                                        WriteTrafficAssumptions(4))


class WritePolicyExplainerTest(unittest.TestCase):
    def test_all_seven_decision_kinds_are_reachable_without_unknown(self):
        read = session((MemoryAccess(MemoryAccessKind.READ, 0),
                        MemoryAccess(MemoryAccessKind.READ, 0)))
        read_steps = read.run_all()
        write = session((MemoryAccess(MemoryAccessKind.READ, 0),
                         MemoryAccess(MemoryAccessKind.WRITE, 0)))
        write_steps = write.run_all()
        misses = session((MemoryAccess(MemoryAccessKind.WRITE, 0),)).run_all()
        kinds = {
            *(lane.evidence.decision_kind for lane in read_steps[0].lane_steps),
            *(lane.evidence.decision_kind for lane in read_steps[1].lane_steps),
            *(lane.evidence.decision_kind for lane in write_steps[1].lane_steps),
            *(lane.evidence.decision_kind for lane in misses[0].lane_steps),
        }
        self.assertEqual(kinds, set(WriteDecisionKind))
        self.assertNotIn("UNKNOWN", WriteDecisionKind.__members__)
        self.assertNotIn("OTHER", WriteDecisionKind.__members__)

    def test_bypass_has_no_fill_or_eviction_and_preserves_snapshot(self):
        step = session((MemoryAccess(MemoryAccessKind.WRITE, 0),)).step()
        for lane_step in (step.lane_steps[1], step.lane_steps[3]):
            evidence = lane_step.evidence
            self.assertTrue(evidence.bypassed)
            self.assertIsNone(evidence.fill_way)
            self.assertIsNone(evidence.evicted_way)
            self.assertEqual(lane_step.before_cache_snapshot, lane_step.after_cache_snapshot)
            self.assertTrue(evidence.metadata_consistent)

    def test_dirty_and_clean_victim_evidence_uses_formal_evicted_way(self):
        comparison = session((MemoryAccess(MemoryAccessKind.WRITE, 0),
                              MemoryAccess(MemoryAccessKind.WRITE, 16)))
        step = comparison.run_all()[1]
        clean = step.lane_steps[0].evidence
        dirty = step.lane_steps[2].evidence
        self.assertEqual((clean.evicted_way, clean.victim_tag, clean.victim_dirty), (0, 0, False))
        self.assertEqual((dirty.evicted_way, dirty.victim_tag, dirty.victim_dirty), (0, 0, True))
        self.assertEqual(clean.traffic_delta.dirty_writebacks, 0)
        self.assertEqual(dirty.traffic_delta.dirty_writebacks, 1)

    def test_invalid_fill_has_no_eviction(self):
        evidence = session((MemoryAccess(MemoryAccessKind.READ, 0),)).step().lane_steps[0].evidence
        self.assertEqual(evidence.fill_way, 0)
        self.assertIsNone(evidence.evicted_way)
        self.assertIsNone(evidence.victim_tag)

    def test_metadata_consistent_is_computed_from_result_and_snapshots(self):
        lane = WRITE_POLICY_LANES[0]
        config = CacheConfig(16, 16, 1)
        core = CacheSimulator(config)
        before = snapshot_cache(core.get_cache_snapshot())
        result = core.access(0, "read")
        after = snapshot_cache(core.get_cache_snapshot())
        tampered = dict(result)
        tampered["operation"] = "write"
        evidence = WritePolicyExplainer.explain(
            lane, MemoryAccess(MemoryAccessKind.READ, 0), WriteTrafficAssumptions(4),
            config, before, tampered, after,
        )
        self.assertFalse(evidence.metadata_consistent)

    def test_snapshot_and_evidence_are_frozen_value_data(self):
        lane_step = session((MemoryAccess(MemoryAccessKind.READ, 0),)).step().lane_steps[0]
        with self.assertRaises(FrozenInstanceError):
            lane_step.evidence.cache_hit = False
        with self.assertRaises(FrozenInstanceError):
            lane_step.after_cache_snapshot[0].valid = False


if __name__ == "__main__":
    unittest.main()
