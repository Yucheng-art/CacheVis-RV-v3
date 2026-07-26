"""Session boundaries and synchronized policy-lane behavior."""

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.policy import (
    DIRECT_MAPPED_CONTROL,
    LRU_ADVANTAGE,
    PolicyComparisonSession,
    PolicyDecisionKind,
)


class PolicySessionTest(unittest.TestCase):
    def test_policies_order_and_config_are_stable(self):
        config = LRU_ADVANTAGE.config
        session = PolicyComparisonSession(config, LRU_ADVANTAGE.addresses)
        self.assertEqual(session.policies, ("LRU", "FIFO", "Random"))
        self.assertIs(session.config, config)
        self.assertEqual(config.replacement_policy, "LRU")

    def test_each_step_uses_same_address_set_and_tag(self):
        session = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        for step in session.run_all():
            for lane in step.lane_steps:
                self.assertEqual(lane.decision.set_index, step.set_index)
                self.assertEqual(lane.decision.tag, step.tag)
            self.assertEqual(step.address_hex, f"0x{step.address:X}")

    def test_before_after_snapshots_are_complete_and_immutable(self):
        session = PolicyComparisonSession(LRU_ADVANTAGE.config, [0])
        step = session.step()
        for lane in step.lane_steps:
            self.assertEqual(len(lane.before_set_lines), 2)
            self.assertEqual(len(lane.after_set_lines), 2)
            self.assertTrue(all(not line.valid for line in lane.before_set_lines))
            self.assertEqual(
                lane.decision.decision_kind, PolicyDecisionKind.INVALID_FILL
            )
        snapshot = session.get_cache_snapshot("LRU")
        self.assertIsInstance(snapshot, tuple)
        with self.assertRaises(TypeError):
            snapshot[0] = ()
        with self.assertRaises(FrozenInstanceError):
            snapshot[0][0].valid = False

    def test_snapshot_cannot_mutate_session_and_lanes_are_independent(self):
        session = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        session.run_all()
        snapshots = dict(session.get_all_cache_snapshots())
        self.assertEqual(set(snapshots), {"LRU", "FIFO", "Random"})
        self.assertNotEqual(snapshots["LRU"], snapshots["FIFO"])
        self.assertEqual(session.get_cache_snapshot("LRU"), snapshots["LRU"])

    def test_step_and_run_all_and_reset_are_reproducible(self):
        stepped = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        while stepped.has_next():
            stepped.step()
        run = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        self.assertEqual(stepped.steps, run.run_all())
        first = run.steps
        run.reset()
        self.assertEqual(run.statistics.accesses, 0)
        self.assertEqual(run.run_all(), first)

    def test_empty_trace_and_completion_semantics(self):
        session = PolicyComparisonSession(LRU_ADVANTAGE.config, [])
        self.assertTrue(session.is_complete)
        self.assertEqual(session.run_all(), ())
        with self.assertRaises(StopIteration):
            session.step()
        completed = PolicyComparisonSession(LRU_ADVANTAGE.config, [0])
        completed.run_all()
        self.assertEqual(len(completed.run_all()), 1)
        with self.assertRaises(StopIteration):
            completed.step()

    def test_invalid_addresses_are_rejected(self):
        with self.assertRaises(ValueError):
            PolicyComparisonSession(LRU_ADVANTAGE.config, [-1])
        small = CacheConfig(
            cache_size_bytes=2, block_size_bytes=1, ways=2,
            address_bits=4,
        )
        with self.assertRaisesRegex(ValueError, "4-bit"):
            PolicyComparisonSession(small, [16])
        with self.assertRaises(TypeError):
            PolicyComparisonSession(small, [True])

    def test_direct_mapped_has_one_identical_victim_candidate(self):
        steps = PolicyComparisonSession(
            DIRECT_MAPPED_CONTROL.config,
            DIRECT_MAPPED_CONTROL.addresses,
        ).run_all()
        for step in steps[1:]:
            victims = {
                lane.decision.victim_way for lane in step.lane_steps
            }
            self.assertEqual(victims, {0})
            self.assertFalse(step.victim_diverged)
            self.assertFalse(step.state_diverged)

    def test_lru_hit_updates_recency_but_fifo_hit_keeps_insertion_time(self):
        session = PolicyComparisonSession(LRU_ADVANTAGE.config, [0, 1, 0])
        third = session.run_all()[2]
        lanes = {lane.policy: lane for lane in third.lane_steps}
        lru_before = next(
            line for line in lanes["LRU"].before_set_lines if line.way == 0
        )
        lru_after = next(
            line for line in lanes["LRU"].after_set_lines if line.way == 0
        )
        fifo_before = next(
            line for line in lanes["FIFO"].before_set_lines if line.way == 0
        )
        fifo_after = next(
            line for line in lanes["FIFO"].after_set_lines if line.way == 0
        )
        self.assertGreater(lru_after.last_used, lru_before.last_used)
        self.assertEqual(fifo_after.insert_time, fifo_before.insert_time)


if __name__ == "__main__":
    unittest.main()
