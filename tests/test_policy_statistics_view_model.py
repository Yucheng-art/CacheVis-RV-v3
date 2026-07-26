import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.policy import (
    LRU_ADVANTAGE,
    PolicyController,
)


class PolicyStatisticsViewModelTest(unittest.TestCase):
    def test_initial_statistics_are_zero_for_all_lanes(self):
        state = PolicyController().start_session(
            LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses
        )
        view = state.statistics_view
        self.assertEqual(0, view.accesses)
        self.assertEqual(("LRU", "FIFO", "Random"), tuple(lane.policy for lane in view.lane_statistics))
        self.assertTrue(all(lane.accesses == lane.hits == lane.misses == 0 for lane in view.lane_statistics))

    def test_final_lane_statistics_and_invariants_match_formal_statistics(self):
        controller = PolicyController()
        controller.start_session(LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses)
        state = controller.run_all()
        lanes = {lane.policy: lane for lane in state.statistics_view.lane_statistics}
        self.assertEqual((2, 3), (lanes["LRU"].hits, lanes["LRU"].misses))
        self.assertEqual((1, 4), (lanes["FIFO"].hits, lanes["FIFO"].misses))
        for lane in lanes.values():
            self.assertTrue(lane.access_invariant_ok)
            self.assertTrue(lane.miss_partition_invariant_ok)
        self.assertTrue(state.statistics_view.outcome_partition_invariant_ok)

    def test_historical_selection_does_not_rewind_statistics(self):
        controller = PolicyController()
        controller.start_session(LRU_ADVANTAGE.config, LRU_ADVANTAGE.addresses)
        latest = controller.run_all()
        selected = controller.select_step(0)
        self.assertEqual(latest.statistics, selected.statistics)
        self.assertEqual(latest.statistics_view, selected.statistics_view)


if __name__ == "__main__":
    unittest.main()
