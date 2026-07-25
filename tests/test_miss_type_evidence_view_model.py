"""Tests for stable evidence-chain presentation models."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.miss_type import (
    CAPACITY_PRESET,
    CONFLICT_PRESET,
    MissType,
    MissTypeSession,
    build_evidence_view_model,
)


class MissTypeEvidenceViewModelTest(unittest.TestCase):
    def test_compulsory_rule_path(self):
        step = MissTypeSession(CONFLICT_PRESET.config, (0,)).step()
        model = build_evidence_view_model(step)

        self.assertEqual(
            model.rule_path,
            ("First access to this memory block", "Compulsory Miss"),
        )
        self.assertEqual(model.classification_title, "Compulsory Miss")

    def test_conflict_rule_path(self):
        step = MissTypeSession(
            CONFLICT_PRESET.config,
            CONFLICT_PRESET.addresses,
        ).run_all()[-1]
        model = build_evidence_view_model(step)

        self.assertEqual(
            model.rule_path,
            (
                "This block was seen before",
                "Actual Cache Miss",
                "Fully Associative Reference Hit",
                "Conflict Miss",
            ),
        )
        self.assertIs(model.miss_type, MissType.CONFLICT)

    def test_capacity_rule_path(self):
        step = MissTypeSession(
            CAPACITY_PRESET.config,
            CAPACITY_PRESET.addresses,
        ).run_all()[-1]
        model = build_evidence_view_model(step)

        self.assertEqual(model.rule_path[-2:], (
            "Fully Associative Reference Miss",
            "Capacity Miss",
        ))
        self.assertIs(model.miss_type, MissType.CAPACITY)

    def test_hit_rule_path_has_no_miss_type(self):
        steps = MissTypeSession(CONFLICT_PRESET.config, (0, 0)).run_all()
        model = build_evidence_view_model(steps[-1])

        self.assertEqual(
            model.rule_path,
            ("Actual Cache Hit", "No miss classification"),
        )
        self.assertIsNone(model.miss_type)
        self.assertEqual(model.classification_title, "Cache Hit")

    def test_reason_is_the_classifier_evidence_reason(self):
        step = MissTypeSession(CONFLICT_PRESET.config, (0,)).step()
        model = build_evidence_view_model(step)

        self.assertEqual(
            model.classification_reason,
            step.evidence.classification_reason,
        )

    def test_statuses_and_seen_before_are_derived_from_step(self):
        step = MissTypeSession(
            CONFLICT_PRESET.config,
            CONFLICT_PRESET.addresses,
        ).run_all()[-1]
        model = build_evidence_view_model(step)

        self.assertEqual(model.actual_status, "Miss")
        self.assertEqual(model.reference_status, "Hit")
        self.assertTrue(model.seen_before)

    def test_no_evidence_model_contains_unknown(self):
        sessions = (
            MissTypeSession(CONFLICT_PRESET.config, (0, 0)),
            MissTypeSession(CONFLICT_PRESET.config, CONFLICT_PRESET.addresses),
            MissTypeSession(CAPACITY_PRESET.config, CAPACITY_PRESET.addresses),
        )

        for session in sessions:
            for step in session.run_all():
                model = build_evidence_view_model(step)
                self.assertNotIn("unknown", repr(model).lower())


if __name__ == "__main__":
    unittest.main()
