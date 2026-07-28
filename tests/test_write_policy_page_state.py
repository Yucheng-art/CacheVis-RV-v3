import dataclasses
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import (
    WRITE_POLICY_PRESETS, WritePolicyController, empty_write_policy_page_state,
)


class WritePolicyPageStateTest(unittest.TestCase):
    def test_empty_and_loaded_state_contract(self):
        empty = empty_write_policy_page_state()
        self.assertFalse(empty.has_experiment)
        self.assertEqual(empty.accesses, ())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            empty.has_experiment = True
        state = WritePolicyController().load_preset(WRITE_POLICY_PRESETS[0])
        self.assertTrue(state.has_experiment)
        self.assertEqual(len(state.lanes), 4)
        self.assertIsInstance(state.accesses, tuple)

    def test_empty_trace_is_complete_without_selection(self):
        preset = WRITE_POLICY_PRESETS[0]
        state = WritePolicyController().load_experiment(
            preset.config, (), preset.assumptions
        )
        self.assertTrue(state.is_complete)
        self.assertIsNone(state.latest_step)
        self.assertIsNone(state.selected_step)


if __name__ == "__main__":
    unittest.main()
