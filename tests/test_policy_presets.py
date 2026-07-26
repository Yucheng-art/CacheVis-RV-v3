"""Stable Policy comparison preset tests."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    DIRECT_MAPPED_CONTROL,
    FIFO_ADVANTAGE,
    LRU_ADVANTAGE,
    NO_REPLACEMENT_PRESSURE,
    POLICY_PRESETS,
    SEEDED_RANDOM_REPLAY,
    SET_LOCAL_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyComparisonSession,
    PolicyDecisionKind,
)


def stats_by_policy(preset):
    session = PolicyComparisonSession(
        preset.config, preset.addresses, preset.random_seed
    )
    session.run_all()
    return session, {
        lane.policy: lane for lane in session.statistics.lane_statistics
    }


class PolicyPresetsTest(unittest.TestCase):
    def test_seven_presets_are_immutable_and_stably_ordered(self):
        self.assertEqual(len(POLICY_PRESETS), 7)
        self.assertEqual(
            tuple(preset.preset_id for preset in POLICY_PRESETS),
            (
                "no_replacement_pressure",
                "victim_divergence_before_outcome",
                "lru_advantage",
                "fifo_advantage",
                "set_local_pressure",
                "direct_mapped_control",
                "seeded_random_replay",
            ),
        )

    def test_lru_fifo_expected_totals_for_every_preset(self):
        for preset in POLICY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                _, lanes = stats_by_policy(preset)
                self.assertEqual(
                    (lanes["LRU"].hits, lanes["LRU"].misses),
                    (preset.expected_lru_hits, preset.expected_lru_misses),
                )
                self.assertEqual(
                    (lanes["FIFO"].hits, lanes["FIFO"].misses),
                    (preset.expected_fifo_hits, preset.expected_fifo_misses),
                )

    def test_no_pressure_has_no_eviction(self):
        session, lanes = stats_by_policy(NO_REPLACEMENT_PRESSURE)
        self.assertTrue(all(lane.evictions == 0 for lane in lanes.values()))
        self.assertFalse(any(step.state_diverged for step in session.steps))

    def test_victim_divergence_expected_victim_tags(self):
        session, _ = stats_by_policy(VICTIM_DIVERGENCE_BEFORE_OUTCOME)
        fourth = session.steps[3]
        evidence = {lane.policy: lane.decision for lane in fourth.lane_steps}
        self.assertEqual(evidence["LRU"].victim_tag, 1)
        self.assertEqual(evidence["FIFO"].victim_tag, 0)
        self.assertFalse(fourth.outcome_diverged)
        self.assertTrue(fourth.victim_diverged)
        self.assertTrue(fourth.state_diverged)

    def test_lru_and_fifo_advantage_outcomes(self):
        lru_session, _ = stats_by_policy(LRU_ADVANTAGE)
        final = {lane.policy: lane.cache_hit for lane in lru_session.steps[-1].lane_steps}
        self.assertTrue(final["LRU"])
        self.assertFalse(final["FIFO"])
        fifo_session, _ = stats_by_policy(FIFO_ADVANTAGE)
        final = {lane.policy: lane.cache_hit for lane in fifo_session.steps[-1].lane_steps}
        self.assertFalse(final["LRU"])
        self.assertTrue(final["FIFO"])
        self.assertNotIn("always", FIFO_ADVANTAGE.expected_teaching_conclusion.lower())

    def test_set_local_pressure_leaves_other_set_invalid(self):
        session, _ = stats_by_policy(SET_LOCAL_PRESSURE)
        for policy, snapshot in session.get_all_cache_snapshots():
            with self.subTest(policy=policy):
                self.assertTrue(all(not line.valid for line in snapshot[1]))

    def test_direct_mapped_lanes_remain_identical(self):
        session, _ = stats_by_policy(DIRECT_MAPPED_CONTROL)
        self.assertTrue(all(not step.outcome_diverged for step in session.steps))
        self.assertTrue(all(not step.victim_diverged for step in session.steps))
        self.assertTrue(all(not step.state_diverged for step in session.steps))

    def test_seeded_random_victims_are_legal(self):
        session, _ = stats_by_policy(SEEDED_RANDOM_REPLAY)
        random_evictions = [
            lane.decision for step in session.steps for lane in step.lane_steps
            if lane.policy == "Random"
            and lane.decision.decision_kind is PolicyDecisionKind.EVICTION
        ]
        self.assertTrue(random_evictions)
        self.assertTrue(all(
            evidence.victim_way in evidence.random_candidate_ways
            for evidence in random_evictions
        ))


if __name__ == "__main__":
    unittest.main()
