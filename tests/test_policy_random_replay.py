"""Seeded Random replay and process-global state isolation."""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    SEEDED_RANDOM_REPLAY,
    IsolatedRandomStream,
    PolicyComparisonSession,
    PolicyDecisionKind,
)


def random_lane(steps):
    return tuple(
        next(lane for lane in step.lane_steps if lane.policy == "Random")
        for step in steps
    )


class PolicyRandomReplayTest(unittest.TestCase):
    def make(self, seed=2026):
        return PolicyComparisonSession(
            SEEDED_RANDOM_REPLAY.config,
            SEEDED_RANDOM_REPLAY.addresses,
            seed,
        )

    def test_same_seed_and_new_sessions_are_identical(self):
        first = self.make().run_all()
        second = self.make().run_all()
        self.assertEqual(random_lane(first), random_lane(second))

    def test_reset_and_step_run_all_are_identical(self):
        session = self.make()
        first = session.run_all()
        session.reset()
        self.assertEqual(random_lane(first), random_lane(session.run_all()))
        stepped = self.make()
        while stepped.has_next():
            stepped.step()
        self.assertEqual(random_lane(first), random_lane(stepped.steps))

    def test_seed_is_public_and_recorded_in_random_evidence(self):
        session = self.make(77)
        self.assertEqual(session.random_seed, 77)
        draw_indexes = []
        for step in session.run_all():
            lane = next(lane for lane in step.lane_steps if lane.policy == "Random")
            self.assertEqual(lane.decision.random_seed, 77)
            if lane.decision.decision_kind is PolicyDecisionKind.EVICTION:
                draw_indexes.append(lane.decision.random_draw_index)
            else:
                self.assertIsNone(lane.decision.random_draw_index)
        self.assertEqual(draw_indexes, list(range(len(draw_indexes))))

    def test_random_lane_does_not_pollute_global_state(self):
        random.seed(991)
        before = random.getstate()
        self.make().run_all()
        self.assertEqual(random.getstate(), before)

    def test_exception_also_restores_global_state(self):
        random.seed(123)
        before = random.getstate()
        stream = IsolatedRandomStream(2026)

        def fail():
            random.randrange(10)
            raise RuntimeError("expected failure")

        with self.assertRaisesRegex(RuntimeError, "expected"):
            stream.run(fail)
        self.assertEqual(random.getstate(), before)

    def test_random_evictions_are_not_described_as_lru_or_fifo(self):
        evictions = [
            lane.decision
            for step in self.make().run_all()
            for lane in step.lane_steps
            if lane.policy == "Random"
            and lane.decision.decision_kind is PolicyDecisionKind.EVICTION
        ]
        self.assertTrue(evictions)
        for evidence in evictions:
            self.assertIsNone(evidence.selected_metric)
            self.assertEqual(
                evidence.random_candidate_ways, evidence.valid_ways_before
            )
            self.assertNotIn("least-recently", evidence.classification_reason)
            self.assertNotIn("oldest-inserted", evidence.classification_reason)


if __name__ == "__main__":
    unittest.main()
