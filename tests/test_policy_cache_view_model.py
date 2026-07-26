import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.core import CacheLine
from cachevis_rv.labs.policy import (
    NO_REPLACEMENT_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyController,
)


class PolicyCacheViewModelTest(unittest.TestCase):
    def test_initial_lines_have_stable_policy_set_way_order(self):
        preset = NO_REPLACEMENT_PRESSURE
        state = PolicyController().start_session(preset.config, preset.addresses)
        self.assertEqual(("LRU", "FIFO", "Random"), tuple(lane.policy for lane in state.lane_caches))
        for lane in state.lane_caches:
            self.assertEqual(2, len(lane.cache_lines))
            self.assertEqual([(0, 0), (0, 1)], [(line.set_index, line.way) for line in lane.cache_lines])
            self.assertTrue(all(not line.valid for line in lane.cache_lines))

    def test_invalid_fill_marker_and_changed_line_are_formal(self):
        controller = PolicyController()
        controller.start_session(NO_REPLACEMENT_PRESSURE.config, NO_REPLACEMENT_PRESSURE.addresses)
        state = controller.step()
        for lane in state.lane_caches:
            marked = [line for line in lane.cache_lines if line.is_fill_way]
            self.assertEqual([0], [line.way for line in marked])
            self.assertTrue(marked[0].is_changed_by_current_access)
            self.assertFalse(any(line.is_victim_way for line in lane.cache_lines))

    def test_hit_marker_uses_current_decision(self):
        controller = PolicyController()
        controller.start_session(NO_REPLACEMENT_PRESSURE.config, NO_REPLACEMENT_PRESSURE.addresses)
        controller.step()
        controller.step()
        state = controller.step()
        for lane in state.lane_caches:
            self.assertTrue(lane.current_cache_hit)
            self.assertEqual([0], [line.way for line in lane.cache_lines if line.is_hit_way])
            self.assertFalse(any(line.is_fill_way or line.is_victim_way for line in lane.cache_lines))

    def test_eviction_victim_eligible_and_changed_markers(self):
        preset = VICTIM_DIVERGENCE_BEFORE_OUTCOME
        controller = PolicyController()
        controller.start_session(preset.config, preset.addresses)
        state = controller.run_all()
        for lane in state.lane_caches:
            victim = next(line for line in lane.cache_lines if line.is_victim_way)
            self.assertTrue(victim.is_eligible_victim)
            self.assertTrue(victim.is_valid_candidate)
            self.assertTrue(victim.is_changed_by_current_access)
            self.assertEqual(lane.current_victim_way, victim.way)

    def test_view_models_do_not_expose_cache_line(self):
        state = PolicyController().start_session(
            NO_REPLACEMENT_PRESSURE.config,
            NO_REPLACEMENT_PRESSURE.addresses,
        )
        self.assertFalse(any(isinstance(line, CacheLine) for lane in state.lane_caches for line in lane.cache_lines))
        self.assertTrue(all(isinstance(lane.cache_lines, tuple) for lane in state.lane_caches))

    def test_historical_selection_does_not_rollback_cache(self):
        preset = VICTIM_DIVERGENCE_BEFORE_OUTCOME
        controller = PolicyController()
        controller.start_session(preset.config, preset.addresses)
        latest = controller.run_all()
        selected = controller.select_step(0)
        self.assertEqual(latest.lane_caches, selected.lane_caches)


if __name__ == "__main__":
    unittest.main()
