import dataclasses
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import WRITE_POLICY_PRESETS, WritePolicyController


class WritePolicyDecisionViewModelTest(unittest.TestCase):
    def test_four_lanes_and_miss_semantics(self):
        controller = WritePolicyController()
        state = controller.load_preset(WRITE_POLICY_PRESETS[2])
        decisions = controller.step().selected_lane_decisions
        self.assertEqual(tuple(item.lane_id for item in decisions),
                         ("wt_wa", "wt_nwa", "wb_wa", "wb_nwa"))
        self.assertTrue(all(item.result_label == "MISS" for item in decisions))
        self.assertEqual(tuple(item.bypassed for item in decisions),
                         (False, True, False, True))
        self.assertTrue(all(item.metadata_consistent for item in decisions))
        self.assertTrue(all(item.traffic.transaction_decomposition_ok for item in decisions))

    def test_all_seven_decision_kinds_and_frozen_contract(self):
        kinds = set()
        sample = None
        for preset in WRITE_POLICY_PRESETS:
            controller = WritePolicyController()
            controller.load_preset(preset)
            state = controller.run_all()
            for timeline_step in state.timeline_steps:
                controller.select_step(timeline_step.step_index)
                kinds.update(item.decision_kind for item in controller.state.selected_lane_decisions)
                sample = controller.state.selected_lane_decisions[0]
        self.assertEqual(len(kinds), 7)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            sample.result_label = "OTHER"


if __name__ == "__main__":
    unittest.main()
