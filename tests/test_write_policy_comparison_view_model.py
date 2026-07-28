import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyController


class WritePolicyComparisonViewModelTest(unittest.TestCase):
    def _run(self, index):
        controller = WritePolicyController()
        controller.load_preset(WRITE_POLICY_PRESETS[index])
        return controller.run_all()

    def test_read_only_and_empty_trace_are_stable_four_way_ties(self):
        state = self._run(0)
        self.assertEqual(state.divergence_summary.outcome_divergence_steps, 0)
        self.assertEqual(len(state.comparison_summary.runtime_lowest_traffic_lane_ids), 4)
        preset = WRITE_POLICY_PRESETS[0]
        empty_controller = WritePolicyController()
        empty = empty_controller.load_experiment(preset.config, (), preset.assumptions)
        self.assertEqual(len(empty.comparison_summary.highest_hit_rate_lane_ids), 4)

    def test_formal_preset_observations_and_leaders(self):
        repeated = self._run(1)
        stats = {item.lane_id: item for item in repeated.current_lane_statistics}
        self.assertEqual((stats["wt_wa"].total_lower_memory_bytes,
                          stats["wb_wa"].total_lower_memory_bytes), (36, 16))
        allocate = self._run(2).comparison_summary
        self.assertTrue(allocate.allocation_changed_future_outcome)
        self.assertTrue(allocate.bypass_observed)
        dirty = self._run(3).comparison_summary
        self.assertTrue(dirty.dirty_eviction_observed)
        streaming = self._run(4).comparison_summary
        self.assertNotIn("universally optimal", " ".join(streaming.actual_observations).lower())

    def test_mixed_divergence_counts_and_first_steps(self):
        summary = self._run(6).divergence_summary
        self.assertEqual(
            (summary.outcome_divergence_steps, summary.allocation_divergence_steps,
             summary.bypass_divergence_steps, summary.writeback_divergence_steps,
             summary.traffic_divergence_steps, summary.dirty_state_divergence_steps,
             summary.cache_state_divergence_steps),
            (1, 4, 3, 2, 5, 5, 5),
        )
        self.assertTrue(summary.outcome_partition_ok)
        self.assertEqual(summary.first_allocation_divergence_step, 0)

    def test_caution_is_exact_and_does_not_claim_universal_best(self):
        summary = self._run(4).comparison_summary
        self.assertEqual(summary.caution_note,
            "Results apply only to the current trace, cache configuration, and traffic assumptions.")


if __name__ == "__main__":
    unittest.main()
