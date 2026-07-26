"""Victim, state, and outcome divergence semantics."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.policy import (
    FIFO_ADVANTAGE,
    LRU_ADVANTAGE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyComparisonSession,
    PolicyDecisionKind,
)


class PolicyDivergenceTest(unittest.TestCase):
    def test_victim_and_state_diverge_before_outcome(self):
        steps = PolicyComparisonSession(
            VICTIM_DIVERGENCE_BEFORE_OUTCOME.config,
            VICTIM_DIVERGENCE_BEFORE_OUTCOME.addresses,
        ).run_all()
        fourth = steps[3]
        self.assertFalse(fourth.outcome_diverged)
        self.assertTrue(fourth.victim_diverged)
        self.assertTrue(fourth.state_diverged)
        self.assertEqual(fourth.statistics.outcome_divergence_steps, 0)

    def test_lru_advantage_later_diverges_in_outcome(self):
        steps = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        ).run_all()
        self.assertFalse(steps[3].outcome_diverged)
        self.assertTrue(steps[3].victim_diverged)
        self.assertTrue(steps[4].outcome_diverged)
        hits = {lane.policy: lane.cache_hit for lane in steps[4].lane_steps}
        self.assertTrue(hits["LRU"])
        self.assertFalse(hits["FIFO"])

    def test_fifo_advantage_later_diverges_in_opposite_direction(self):
        final = PolicyComparisonSession(
            FIFO_ADVANTAGE.config, FIFO_ADVANTAGE.addresses
        ).run_all()[-1]
        hits = {lane.policy: lane.cache_hit for lane in final.lane_steps}
        self.assertFalse(hits["LRU"])
        self.assertTrue(hits["FIFO"])
        self.assertTrue(final.outcome_diverged)

    def test_only_one_eviction_does_not_mean_victim_divergence(self):
        config = CacheConfig(
            cache_size_bytes=2, block_size_bytes=1, ways=2
        )
        session = PolicyComparisonSession(config, [0, 1, 0, 2, 1])
        steps = session.run_all()
        final = steps[-1]
        evictions = [
            lane for lane in final.lane_steps
            if lane.decision.decision_kind is PolicyDecisionKind.EVICTION
        ]
        self.assertEqual(len(evictions), 1)
        self.assertFalse(final.victim_diverged)
        self.assertTrue(final.outcome_diverged)

    def test_state_divergence_compares_full_snapshot_and_can_persist(self):
        session = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses + (3, 4)
        )
        steps = session.run_all()
        self.assertTrue(any(step.state_diverged for step in steps))
        self.assertEqual(
            session.statistics.all_agree_steps
            + session.statistics.outcome_divergence_steps,
            len(steps),
        )


if __name__ == "__main__":
    unittest.main()
