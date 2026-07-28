import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyController


class WritePolicyControllerTest(unittest.TestCase):
    def test_initial_load_step_and_run_all_lifecycle(self):
        controller = WritePolicyController()
        self.assertFalse(controller.state.has_experiment)
        state = controller.load_preset(WRITE_POLICY_PRESETS[-1])
        self.assertTrue(state.has_experiment)
        self.assertEqual(state.next_step_index, 0)
        self.assertEqual(len(state.current_lane_caches), 4)
        self.assertTrue(all(not line.valid for lane in state.current_lane_caches for line in lane.lines))
        state = controller.step()
        self.assertEqual((state.latest_step_index, state.selected_step_index), (0, 0))
        state = controller.run_all()
        self.assertTrue(state.is_complete)
        self.assertEqual(state.next_step_index, state.total_steps)
        self.assertEqual(state, controller.run_all())

    def test_all_presets_load_and_run(self):
        for preset in WRITE_POLICY_PRESETS:
            controller = WritePolicyController()
            state = controller.load_preset(preset)
            self.assertEqual(state.experiment_id, preset.preset_id)
            self.assertEqual(controller.run_all().next_step_index, len(preset.accesses))

    def test_selection_does_not_change_current_run_state(self):
        controller = WritePolicyController()
        controller.load_preset(WRITE_POLICY_PRESETS[-1])
        latest = controller.run_all()
        evidence = (latest.current_lane_caches, latest.current_lane_statistics,
                    latest.next_step_index)
        selected = controller.select_step(0)
        self.assertEqual((selected.selected_step_index, selected.latest_step_index), (0, 4))
        self.assertEqual(
            (selected.current_lane_caches, selected.current_lane_statistics,
             selected.next_step_index), evidence)
        self.assertEqual(controller.select_latest().selected_step_index, 4)

    def test_reset_clear_and_invalid_operations(self):
        controller = WritePolicyController()
        with self.assertRaises(RuntimeError):
            controller.step()
        controller.load_preset(WRITE_POLICY_PRESETS[0])
        with self.assertRaises(ValueError):
            controller.select_latest()
        controller.run_all()
        with self.assertRaises(ValueError):
            controller.select_step(99)
        reset = controller.reset()
        self.assertTrue(reset.has_experiment)
        self.assertEqual(reset.timeline_steps, ())
        self.assertFalse(any(line.valid for lane in reset.current_lane_caches for line in lane.lines))
        self.assertFalse(controller.clear().has_experiment)


if __name__ == "__main__":
    unittest.main()
