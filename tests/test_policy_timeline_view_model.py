import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    LRU_ADVANTAGE,
    NO_REPLACEMENT_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyController,
)


class PolicyTimelineViewModelTest(unittest.TestCase):
    def test_three_badges_and_h_i_e_codes_are_present(self):
        controller = PolicyController()
        controller.start_session(
            NO_REPLACEMENT_PRESSURE.config,
            NO_REPLACEMENT_PRESSURE.addresses,
        )
        state = controller.run_all()
        self.assertTrue(all(len(item.lane_badges) == 3 for item in state.timeline_items))
        self.assertEqual(("I", "I", "I"), tuple(b.decision_code for b in state.timeline_items[0].lane_badges))
        self.assertEqual(("H", "H", "H"), tuple(b.decision_code for b in state.timeline_items[2].lane_badges))

        eviction = PolicyController()
        eviction.start_session(
            VICTIM_DIVERGENCE_BEFORE_OUTCOME.config,
            VICTIM_DIVERGENCE_BEFORE_OUTCOME.addresses,
        )
        final = eviction.run_all().timeline_items[-1]
        self.assertEqual(("E", "E", "E"), tuple(b.decision_code for b in final.lane_badges))

    def test_divergence_codes_are_independent_and_tooltip_is_explicit(self):
        controller = PolicyController()
        controller.start_session(LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses)
        state = controller.run_all()
        victim_item = state.timeline_items[3]
        outcome_item = state.timeline_items[4]
        self.assertIn("VS", victim_item.short_summary)
        self.assertIn("OS", outcome_item.short_summary)
        for phrase in ("Outcome divergence", "Victim divergence", "State divergence"):
            self.assertIn(phrase, victim_item.tooltip)
        for policy in ("LRU", "FIFO", "Random"):
            self.assertIn(policy, victim_item.tooltip)

    def test_current_and_selected_markers_are_independent(self):
        controller = PolicyController()
        controller.start_session(LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses)
        latest = controller.run_all()
        self.assertTrue(latest.timeline_items[-1].is_current)
        self.assertTrue(latest.timeline_items[-1].is_selected)
        selected = controller.select_step(1)
        self.assertTrue(selected.timeline_items[-1].is_current)
        self.assertFalse(selected.timeline_items[-1].is_selected)
        self.assertTrue(selected.timeline_items[1].is_selected)
        self.assertFalse(selected.timeline_items[1].is_current)

    def test_next_step_restores_current_selected_to_new_latest(self):
        controller = PolicyController()
        controller.start_session(LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses)
        controller.step()
        controller.step()
        controller.select_step(0)
        state = controller.step()
        self.assertEqual(2, state.current_step.step_index)
        self.assertEqual(2, state.selected_step.step_index)
        self.assertTrue(state.timeline_items[-1].is_current)
        self.assertTrue(state.timeline_items[-1].is_selected)


if __name__ == "__main__":
    unittest.main()
