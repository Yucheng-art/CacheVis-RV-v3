"""Exact results for all seven write-policy teaching presets."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import (
    WRITE_POLICY_PRESETS, WritePolicyComparisonSession, get_write_policy_preset,
)


class WritePolicyPresetsTest(unittest.TestCase):
    def test_ids_are_unique_and_order_is_stable(self):
        ids = tuple(preset.preset_id for preset in WRITE_POLICY_PRESETS)
        self.assertEqual(ids, (
            "read_only_control", "repeated_resident_writes", "allocate_vs_bypass",
            "dirty_eviction", "streaming_stores", "read_after_write_reuse",
            "mixed_dirty_conflict",
        ))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIs(get_write_policy_preset(ids[0]), WRITE_POLICY_PRESETS[0])

    def test_every_expected_lane_summary_matches_actual_statistics(self):
        for preset in WRITE_POLICY_PRESETS:
            with self.subTest(preset=preset.preset_id):
                session = WritePolicyComparisonSession(
                    preset.config, preset.accesses, preset.assumptions
                )
                session.run_all()
                actual = {stat.lane.lane_id: stat for stat in session.statistics.lane_statistics}
                self.assertEqual(tuple(actual), ("wt_wa", "wt_nwa", "wb_wa", "wb_nwa"))
                for lane_id, expected_pairs in preset.expected_lane_summary:
                    for field, expected in expected_pairs:
                        self.assertEqual(getattr(actual[lane_id], field), expected,
                                         f"{preset.preset_id}/{lane_id}/{field}")

    def test_read_only_has_no_divergence_and_identical_traffic(self):
        session = WritePolicyComparisonSession(
            WRITE_POLICY_PRESETS[0].config,
            WRITE_POLICY_PRESETS[0].accesses,
            WRITE_POLICY_PRESETS[0].assumptions,
        )
        steps = session.run_all()
        self.assertTrue(all(not any((step.outcome_diverged, step.allocation_diverged,
                                    step.bypass_diverged, step.writeback_diverged,
                                    step.traffic_diverged, step.dirty_state_diverged,
                                    step.cache_state_diverged)) for step in steps))

    def test_allocate_bypass_dirty_eviction_streaming_and_mixed_conclusions(self):
        sessions = {}
        for preset in WRITE_POLICY_PRESETS[2:]:
            session = WritePolicyComparisonSession(preset.config, preset.accesses,
                                                   preset.assumptions)
            session.run_all()
            sessions[preset.preset_id] = session
        allocation_steps = sessions["allocate_vs_bypass"].steps
        self.assertTrue(allocation_steps[0].allocation_diverged)
        self.assertTrue(allocation_steps[0].bypass_diverged)
        self.assertTrue(allocation_steps[1].outcome_diverged)
        self.assertTrue(sessions["dirty_eviction"].steps[1].writeback_diverged)
        streaming = {s.lane.lane_id: s for s in sessions["streaming_stores"].statistics.lane_statistics}
        self.assertEqual(streaming["wt_nwa"].block_fills, 0)
        mixed = sessions["mixed_dirty_conflict"].statistics
        self.assertGreater(mixed.outcome_divergence_steps, 0)
        self.assertGreater(mixed.dirty_state_divergence_steps, 0)
        self.assertGreater(mixed.traffic_divergence_steps, 0)

    def test_teaching_text_does_not_claim_a_universal_best_policy(self):
        text = " ".join(p.expected_teaching_conclusion.lower()
                        for p in WRITE_POLICY_PRESETS)
        self.assertIn("not a claim that nwa is universally optimal", text)
        self.assertNotIn("always best", text)


if __name__ == "__main__":
    unittest.main()
