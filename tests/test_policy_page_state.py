from dataclasses import FrozenInstanceError
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    EMPTY_PAGE_STATE,
    LRU_ADVANTAGE,
    PolicyController,
)


class PolicyPageStateTest(unittest.TestCase):
    def test_empty_state_has_no_session_values(self):
        state = EMPTY_PAGE_STATE
        self.assertFalse(state.has_session)
        self.assertIsNone(state.config)
        self.assertEqual((), state.addresses)
        self.assertIsNone(state.random_seed)
        self.assertEqual((), state.policies)
        self.assertIsNone(state.next_step_index)

    def test_page_state_and_all_sequence_fields_are_immutable_tuples(self):
        controller = PolicyController()
        state = controller.start_session(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        with self.assertRaises(FrozenInstanceError):
            state.has_session = False
        self.assertIsInstance(state.addresses, tuple)
        self.assertIsInstance(state.policies, tuple)
        self.assertIsInstance(state.timeline_steps, tuple)
        self.assertIsInstance(state.timeline_items, tuple)
        self.assertIsInstance(state.lane_caches, tuple)

    def test_history_selection_preserves_latest_state_fields(self):
        controller = PolicyController()
        controller.start_session(LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses)
        latest = controller.run_all()
        selected = controller.select_step(0)
        self.assertEqual(latest.current_step, selected.current_step)
        self.assertEqual(latest.lane_caches, selected.lane_caches)
        self.assertEqual(latest.statistics_view, selected.statistics_view)
        self.assertEqual(latest.divergence_summary, selected.divergence_summary)
        self.assertEqual(latest.next_step_index, selected.next_step_index)
        self.assertNotEqual(latest.selected_step, selected.selected_step)

    def test_initial_active_state_has_invalid_cache_and_zero_summaries(self):
        controller = PolicyController()
        state = controller.start_session(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        self.assertEqual(3, len(state.lane_caches))
        self.assertTrue(all(not line.valid for lane in state.lane_caches for line in lane.cache_lines))
        self.assertEqual(0, state.statistics_view.accesses)
        self.assertFalse(state.divergence_summary.has_any_state_divergence)
        self.assertEqual(0, state.next_step_index)


if __name__ == "__main__":
    unittest.main()
