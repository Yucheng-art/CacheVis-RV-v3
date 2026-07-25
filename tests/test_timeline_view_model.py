"""Tests for pure Address Visualizer timeline display models."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from timeline_view_model import build_timeline_item
from visualizer_model import AccessStepViewModel


def _step(**overrides):
    values = {
        "step_index": 0,
        "address": 4,
        "address_dec": "4",
        "address_hex": "0x00000004",
        "address_binary": format(4, "032b"),
        "tag_bits": 30,
        "index_bits": 1,
        "offset_bits": 1,
        "tag": 0,
        "index": 0,
        "offset": 0,
        "mapped_set": 0,
        "hit": False,
        "hit_way": None,
        "victim_way": 0,
        "replaced_valid": False,
        "replaced_tag": None,
        "replacement_reason": "invalid-line",
        "miss_type": "compulsory",
        "before_set_lines": [],
        "after_cache_snapshot": [],
        "total_accesses": 1,
        "hits": 0,
        "misses": 1,
        "hit_rate": 0.0,
        "miss_rate": 1.0,
        "explanation_lines": [],
    }
    values.update(overrides)
    return AccessStepViewModel(**values)


class TimelineViewModelTest(unittest.TestCase):
    def test_miss_item_includes_current_label_and_victim_tooltip(self):
        item = build_timeline_item(_step(step_index=3, mapped_set=2, victim_way=1))

        self.assertEqual(item.result, "MISS")
        self.assertEqual(item.miss_type, "compulsory")
        self.assertTrue(item.is_current)
        self.assertIn("CURRENT | Step 3", item.label)
        self.assertIn("MISS | compulsory", item.label)
        self.assertIn("mapped set: 2", item.tooltip_lines)
        self.assertIn("victim way: 1", item.tooltip_lines)

    def test_hit_item_includes_hit_way_and_no_miss_type(self):
        item = build_timeline_item(
            _step(hit=True, hit_way=0, victim_way=None, miss_type=None), is_current=False
        )

        self.assertEqual(item.result, "HIT")
        self.assertEqual(item.miss_type, "-")
        self.assertFalse(item.is_current)
        self.assertNotIn("CURRENT", item.label)
        self.assertIn("HIT | -", item.label)
        self.assertIn("hit way: 0", item.tooltip_lines)
        self.assertIn("victim way: -", item.tooltip_lines)

    def test_unknown_miss_type_is_preserved(self):
        item = build_timeline_item(_step(miss_type="unknown"))

        self.assertEqual(item.miss_type, "unknown")
        self.assertIn("MISS | unknown", item.label)
        self.assertIn("miss type: unknown", item.tooltip_lines)

    def test_selected_marker_can_coexist_with_current_marker(self):
        item = build_timeline_item(_step(step_index=5), is_current=True, is_selected=True)

        self.assertTrue(item.is_current)
        self.assertTrue(item.is_selected)
        self.assertIn("CURRENT | SELECTED | Step 5", item.label)

    def test_selected_marker_without_current_marker(self):
        item = build_timeline_item(_step(step_index=1), is_current=False, is_selected=True)

        self.assertFalse(item.is_current)
        self.assertTrue(item.is_selected)
        self.assertIn("SELECTED | Step 1", item.label)
        self.assertNotIn("CURRENT", item.label)


if __name__ == "__main__":
    unittest.main()
