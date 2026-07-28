import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyController


class WritePolicyTimelineViewModelTest(unittest.TestCase):
    def test_order_traffic_and_latest_selected_markers(self):
        controller = WritePolicyController()
        controller.load_preset(WRITE_POLICY_PRESETS[-1])
        state = controller.run_all()
        self.assertEqual(tuple(item.step_index for item in state.timeline_steps), tuple(range(5)))
        self.assertEqual(sum(item.is_latest for item in state.timeline_steps), 1)
        self.assertTrue(state.timeline_steps[-1].is_selected)
        for step in state.timeline_steps:
            self.assertEqual(tuple(item.lane_id for item in step.lane_traffic),
                             ("wt_wa", "wt_nwa", "wb_wa", "wb_nwa"))
        selected = controller.select_step(0)
        self.assertTrue(selected.timeline_steps[0].is_selected)
        self.assertTrue(selected.timeline_steps[-1].is_latest)
        self.assertFalse(selected.timeline_steps[0].is_latest)

    def test_cumulative_traffic_matches_final_statistics(self):
        controller = WritePolicyController()
        controller.load_preset(WRITE_POLICY_PRESETS[3])
        state = controller.run_all()
        final = state.timeline_steps[-1].lane_traffic
        stats = state.current_lane_statistics
        self.assertEqual(tuple(item.cumulative_runtime_bytes for item in final),
                         tuple(item.total_lower_memory_bytes for item in stats))
        self.assertEqual(tuple(item.cumulative_with_final_drain_bytes for item in final),
                         tuple(item.total_lower_memory_bytes_with_final_drain for item in stats))


if __name__ == "__main__":
    unittest.main()
