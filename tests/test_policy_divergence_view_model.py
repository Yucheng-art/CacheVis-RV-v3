import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    DIRECT_MAPPED_CONTROL,
    FIFO_ADVANTAGE,
    LRU_ADVANTAGE,
    NO_REPLACEMENT_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyController,
)


def _summary(preset, steps=None):
    controller = PolicyController()
    controller.start_session(preset.config, preset.addresses, preset.random_seed)
    if steps is None:
        return controller.run_all().divergence_summary
    state = controller.state
    for _ in range(steps):
        state = controller.step()
    return state.divergence_summary


class PolicyDivergenceViewModelTest(unittest.TestCase):
    def test_no_pressure_and_direct_mapped_have_no_divergence(self):
        for preset in (NO_REPLACEMENT_PRESSURE, DIRECT_MAPPED_CONTROL):
            with self.subTest(preset=preset.preset_id):
                summary = _summary(preset)
                self.assertFalse(summary.has_any_state_divergence)
                self.assertFalse(summary.has_any_victim_divergence)
                self.assertFalse(summary.has_any_outcome_divergence)

    def test_victim_and_state_diverge_without_predicting_outcome(self):
        summary = _summary(VICTIM_DIVERGENCE_BEFORE_OUTCOME)
        self.assertEqual(3, summary.first_victim_divergence_step)
        self.assertEqual(3, summary.first_state_divergence_step)
        self.assertIsNone(summary.first_outcome_divergence_step)
        self.assertFalse(summary.state_before_outcome)
        self.assertIsNone(summary.divergence_lag_steps)
        self.assertIn("Internal", summary.summary_title)

    def test_lru_advantage_state_precedes_outcome_by_one_step(self):
        summary = _summary(LRU_ADVANTAGE)
        self.assertTrue(summary.state_before_outcome)
        self.assertEqual(3, summary.first_state_divergence_step)
        self.assertEqual(4, summary.first_outcome_divergence_step)
        self.assertEqual(1, summary.divergence_lag_steps)

    def test_fifo_advantage_has_same_divergence_timing(self):
        summary = _summary(FIFO_ADVANTAGE)
        self.assertTrue(summary.state_before_outcome)
        self.assertEqual(1, summary.divergence_lag_steps)
        self.assertTrue(summary.latest_outcome_diverged)

    def test_partial_trace_never_predicts_future_divergence(self):
        summary = _summary(LRU_ADVANTAGE, steps=3)
        self.assertFalse(summary.has_any_state_divergence)
        self.assertFalse(summary.has_any_outcome_divergence)
        self.assertIsNone(summary.first_outcome_divergence_step)


if __name__ == "__main__":
    unittest.main()
