"""Tests for pure Miss Type timeline chip models."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.miss_type import (
    CONFLICT_PRESET,
    MissTypeController,
    build_timeline_items,
)


class MissTypeTimelineViewModelTest(unittest.TestCase):
    def setUp(self):
        controller = MissTypeController()
        controller.start_session(CONFLICT_PRESET.config, list(CONFLICT_PRESET.addresses))
        self.state = controller.run_all()

    def test_result_codes_are_h_c_f_a_vocabulary(self):
        items = build_timeline_items(self.state.timeline_steps)

        self.assertEqual(tuple(item.result_code for item in items), ("C", "C", "F", "F"))
        self.assertTrue(all(item.result_code in {"H", "C", "F", "A"} for item in items))

    def test_current_and_selected_are_independent(self):
        items = build_timeline_items(
            self.state.timeline_steps,
            current_step_index=3,
            selected_step_index=0,
        )

        self.assertTrue(items[3].is_current)
        self.assertFalse(items[3].is_selected)
        self.assertTrue(items[0].is_selected)
        self.assertFalse(items[0].is_current)

    def test_default_latest_can_be_current_and_selected(self):
        items = build_timeline_items(
            self.state.timeline_steps,
            current_step_index=3,
            selected_step_index=3,
        )

        self.assertTrue(items[-1].is_current)
        self.assertTrue(items[-1].is_selected)

    def test_tooltip_contains_address_block_and_full_evidence(self):
        item = build_timeline_items(self.state.timeline_steps)[2]
        tooltip = "\n".join(item.tooltip_lines)

        self.assertIn("Address: 0 (0x0)", tooltip)
        self.assertIn("Memory block: 0", tooltip)
        self.assertIn("Actual Cache: MISS", tooltip)
        self.assertIn("Reference Cache: HIT", tooltip)
        self.assertIn("Conflict Miss", tooltip)


if __name__ == "__main__":
    unittest.main()
