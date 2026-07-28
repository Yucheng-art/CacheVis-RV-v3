import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyController


class WritePolicyCacheViewModelTest(unittest.TestCase):
    def test_cold_and_dirty_cache_states_and_counts(self):
        controller = WritePolicyController()
        cold = controller.load_preset(WRITE_POLICY_PRESETS[1])
        self.assertTrue(all(line.state_label == "INVALID"
                            for lane in cold.current_lane_caches for line in lane.lines))
        state = controller.run_all()
        labels = {line.state_label for lane in state.current_lane_caches for line in lane.lines}
        self.assertIn("CLEAN", labels)
        self.assertIn("DIRTY", labels)
        for lane in state.current_lane_caches:
            self.assertEqual(lane.valid_line_count,
                             lane.clean_line_count + lane.dirty_line_count)
            self.assertEqual(lane.dirty_bytes,
                             lane.dirty_line_count * state.config.block_size_bytes)
            self.assertEqual(tuple((line.set_index, line.way) for line in lane.lines),
                             tuple(sorted((line.set_index, line.way) for line in lane.lines)))

    def test_historical_selection_does_not_rewind_cache(self):
        controller = WritePolicyController()
        controller.load_preset(WRITE_POLICY_PRESETS[-1])
        current = controller.run_all().current_lane_caches
        self.assertEqual(controller.select_step(0).current_lane_caches, current)


if __name__ == "__main__":
    unittest.main()
