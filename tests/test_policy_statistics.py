"""Cumulative Policy comparison statistics and invariants."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    LRU_ADVANTAGE,
    SEEDED_RANDOM_REPLAY,
    PolicyComparisonSession,
)


class PolicyStatisticsTest(unittest.TestCase):
    def test_empty_statistics_are_zero_and_partitioned(self):
        stats = PolicyComparisonSession(LRU_ADVANTAGE.config, []).statistics
        self.assertEqual(stats.accesses, 0)
        self.assertEqual(stats.all_agree_steps, 0)
        self.assertEqual(stats.outcome_divergence_steps, 0)
        for lane in stats.lane_statistics:
            self.assertEqual(lane.accesses, 0)
            self.assertEqual(lane.hit_rate, 0.0)
            self.assertEqual(lane.miss_rate, 0.0)

    def test_lane_invariants_hold_after_every_step(self):
        session = PolicyComparisonSession(
            SEEDED_RANDOM_REPLAY.config,
            SEEDED_RANDOM_REPLAY.addresses,
            SEEDED_RANDOM_REPLAY.random_seed,
        )
        while session.has_next():
            stats = session.step().statistics
            for lane in stats.lane_statistics:
                self.assertEqual(lane.hits + lane.misses, lane.accesses)
                self.assertEqual(
                    lane.invalid_fills + lane.evictions, lane.misses
                )
                self.assertGreaterEqual(lane.hit_rate, 0.0)
                self.assertLessEqual(lane.hit_rate, 1.0)
                self.assertGreaterEqual(lane.miss_rate, 0.0)
                self.assertLessEqual(lane.miss_rate, 1.0)
            self.assertEqual(
                stats.all_agree_steps + stats.outcome_divergence_steps,
                stats.accesses,
            )

    def test_victim_and_state_counts_are_independent(self):
        session = PolicyComparisonSession(
            SEEDED_RANDOM_REPLAY.config,
            SEEDED_RANDOM_REPLAY.addresses,
            SEEDED_RANDOM_REPLAY.random_seed,
        )
        session.run_all()
        stats = session.statistics
        self.assertEqual(stats.outcome_divergence_steps, 0)
        self.assertGreaterEqual(stats.victim_divergence_steps, 1)
        self.assertGreaterEqual(stats.state_divergence_steps, 1)
        self.assertNotEqual(
            stats.all_agree_steps + stats.victim_divergence_steps,
            stats.accesses,
        )

    def test_reset_returns_every_counter_to_zero(self):
        session = PolicyComparisonSession(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        session.run_all()
        session.reset()
        self.assertEqual(session.statistics.accesses, 0)
        self.assertTrue(all(
            lane.accesses == lane.hits == lane.misses == 0
            for lane in session.statistics.lane_statistics
        ))


if __name__ == "__main__":
    unittest.main()
