"""Evidence tests for replacement-policy decision explanation."""

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    PolicyDecisionExplainer,
    PolicyDecisionKind,
    PolicyLineSnapshot,
)


def line(way, *, valid=True, tag=None, used=1, inserted=1):
    return PolicyLineSnapshot(0, way, valid, tag, False, used, inserted)


def result(*, hit, way, tag=9, replaced=False, replaced_tag=None):
    return {
        "index": 0, "tag": tag, "hit": hit, "victim_way": way,
        "replaced_valid": replaced, "replaced_tag": replaced_tag,
    }


class PolicyExplainerTest(unittest.TestCase):
    def test_hit_has_no_fill_or_victim(self):
        before = (line(0, tag=9, used=1), line(1, tag=8, used=2))
        after = (line(0, tag=9, used=3), before[1])
        evidence = PolicyDecisionExplainer.explain(
            "LRU", before, result(hit=True, way=0), after
        )
        self.assertIs(evidence.decision_kind, PolicyDecisionKind.HIT)
        self.assertEqual(evidence.hit_way, 0)
        self.assertIsNone(evidence.fill_way)
        self.assertIsNone(evidence.victim_way)
        self.assertIsNone(evidence.victim_tag)
        self.assertTrue(evidence.metadata_consistent)
        self.assertIn(
            "no fill or replacement occurred",
            evidence.classification_reason.lower(),
        )

    def test_invalid_fill_uses_invalid_way_without_eviction(self):
        before = (line(0, valid=False), line(1, tag=8))
        after = (line(0, tag=9, used=3, inserted=3), before[1])
        evidence = PolicyDecisionExplainer.explain(
            "FIFO", before, result(hit=False, way=0), after
        )
        self.assertIs(evidence.decision_kind, PolicyDecisionKind.INVALID_FILL)
        self.assertEqual(evidence.fill_way, 0)
        self.assertIn(0, evidence.invalid_ways_before)
        self.assertIsNone(evidence.victim_way)
        self.assertIsNone(evidence.victim_tag)
        self.assertTrue(evidence.metadata_consistent)
        self.assertIn("no valid line was evicted", evidence.classification_reason)

    def test_lru_eviction_uses_minimum_last_used_and_victim_tag(self):
        before = (line(0, tag=10, used=1), line(1, tag=11, used=4))
        after = (line(0, tag=9, used=5, inserted=5), before[1])
        evidence = PolicyDecisionExplainer.explain(
            "LRU", before,
            result(hit=False, way=0, replaced=True, replaced_tag=10),
            after,
        )
        self.assertIs(evidence.decision_kind, PolicyDecisionKind.EVICTION)
        self.assertEqual(evidence.eligible_victim_ways, (0,))
        self.assertEqual(evidence.victim_tag, 10)
        self.assertEqual(evidence.selected_metric, 1)
        self.assertTrue(evidence.metadata_consistent)

    def test_lru_and_fifo_ties_include_all_eligible_ways(self):
        before = (line(0, tag=10), line(1, tag=11))
        after = (before[0], line(1, tag=9, used=3, inserted=3))
        access = result(hit=False, way=1, replaced=True, replaced_tag=11)
        for policy in ("LRU", "FIFO"):
            with self.subTest(policy=policy):
                evidence = PolicyDecisionExplainer.explain(
                    policy, before, access, after
                )
                self.assertEqual(evidence.eligible_victim_ways, (0, 1))
                self.assertTrue(evidence.metadata_consistent)

    def test_fifo_uses_minimum_insert_time(self):
        before = (
            line(0, tag=10, used=9, inserted=1),
            line(1, tag=11, used=2, inserted=4),
        )
        after = (line(0, tag=9, used=10, inserted=10), before[1])
        evidence = PolicyDecisionExplainer.explain(
            "FIFO", before,
            result(hit=False, way=0, replaced=True, replaced_tag=10),
            after,
        )
        self.assertEqual(evidence.eligible_victim_ways, (0,))
        self.assertEqual(evidence.selected_metric, 1)

    def test_random_candidates_are_all_valid_ways(self):
        before = (line(0, tag=10), line(1, tag=11))
        after = (before[0], line(1, tag=9, used=3, inserted=3))
        evidence = PolicyDecisionExplainer.explain(
            "Random", before,
            result(hit=False, way=1, replaced=True, replaced_tag=11),
            after, random_seed=2026, random_draw_index=3,
        )
        self.assertEqual(evidence.random_candidate_ways, (0, 1))
        self.assertEqual(evidence.eligible_victim_ways, (0, 1))
        self.assertIn(evidence.victim_way, evidence.random_candidate_ways)
        self.assertIsNone(evidence.selected_metric)
        self.assertEqual(evidence.random_seed, 2026)
        self.assertIn("seeded random replay", evidence.classification_reason)

    def test_metadata_consistent_is_computed_not_constant(self):
        before = (line(0, tag=10, used=1), line(1, tag=11, used=4))
        after = (before[0], line(1, tag=9, used=5, inserted=5))
        evidence = PolicyDecisionExplainer.explain(
            "LRU", before,
            result(hit=False, way=1, replaced=True, replaced_tag=11),
            after,
        )
        self.assertFalse(evidence.metadata_consistent)

    def test_snapshots_are_frozen_values(self):
        snapshot = line(0, tag=1)
        with self.assertRaises(FrozenInstanceError):
            snapshot.tag = 2


if __name__ == "__main__":
    unittest.main()
