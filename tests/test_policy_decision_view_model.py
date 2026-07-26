from dataclasses import replace
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    NO_REPLACEMENT_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyComparisonSession,
    build_comparison_evidence_view_model,
    build_lane_decision_view_model,
)


class PolicyDecisionViewModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        session = PolicyComparisonSession(
            VICTIM_DIVERGENCE_BEFORE_OUTCOME.config,
            VICTIM_DIVERGENCE_BEFORE_OUTCOME.addresses,
        )
        cls.steps = session.run_all()

    def test_hit_rule_path_is_exact_and_has_no_fill_or_victim(self):
        view = build_lane_decision_view_model(self.steps[2].lane_steps[0].decision)
        self.assertEqual(("Target tag already exists in the mapped set", "Cache HIT", "No fill or eviction"), view.rule_path)
        self.assertIsNone(view.fill_way)
        self.assertIsNone(view.victim_way)

    def test_invalid_fill_rule_path_is_exact_and_has_no_victim(self):
        view = build_lane_decision_view_model(self.steps[0].lane_steps[0].decision)
        self.assertEqual(("Target tag is absent", "An invalid way is available", "Fill that way", "No valid line is evicted"), view.rule_path)
        self.assertIsNotNone(view.fill_way)
        self.assertIsNone(view.victim_way)

    def test_lru_and_fifo_eviction_paths_and_metrics_are_exact(self):
        lru = build_lane_decision_view_model(self.steps[3].lane_steps[0].decision)
        fifo = build_lane_decision_view_model(self.steps[3].lane_steps[1].decision)
        self.assertEqual("Compare last_used metadata", lru.rule_path[2])
        self.assertEqual("last_used", lru.selected_metric_label)
        self.assertEqual("Compare insert_time metadata", fifo.rule_path[2])
        self.assertEqual("insert_time", fifo.selected_metric_label)

    def test_random_rule_path_has_no_optimal_or_age_claim(self):
        random_view = build_lane_decision_view_model(self.steps[3].lane_steps[2].decision)
        self.assertEqual("All valid ways are candidates", random_view.rule_path[2])
        text = " ".join(random_view.rule_path).lower()
        self.assertNotIn("optimal", text)
        self.assertNotIn("oldest", text)
        self.assertNotIn("least-recently", text)
        self.assertIsNotNone(random_view.random_seed)

    def test_metadata_consistency_false_is_preserved(self):
        evidence = replace(self.steps[3].lane_steps[0].decision, metadata_consistent=False)
        self.assertFalse(build_lane_decision_view_model(evidence).metadata_consistent)

    def test_comparison_lane_order_and_divergence_text_are_stable(self):
        comparison = build_comparison_evidence_view_model(self.steps[3])
        self.assertEqual(("LRU", "FIFO", "Random"), tuple(lane.policy for lane in comparison.lane_decisions))
        self.assertTrue(comparison.victim_diverged)
        self.assertFalse(comparison.outcome_diverged)
        self.assertIn("Victim", comparison.divergence_title)
        self.assertNotIn("unknown", comparison.teaching_insight.lower())

    def test_no_pressure_decisions_never_use_unknown(self):
        session = PolicyComparisonSession(
            NO_REPLACEMENT_PRESSURE.config,
            NO_REPLACEMENT_PRESSURE.addresses,
        )
        text = " ".join(
            build_lane_decision_view_model(lane.decision).decision_title
            for step in session.run_all()
            for lane in step.lane_steps
        )
        self.assertNotIn("unknown", text.lower())


if __name__ == "__main__":
    unittest.main()
