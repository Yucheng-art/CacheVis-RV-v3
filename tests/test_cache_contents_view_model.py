"""Tests for pure cache contents display helpers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_contents_view_model import build_cache_line_card_models, format_tag
from visualizer_model import CacheLineViewModel


class CacheContentsViewModelTest(unittest.TestCase):
    """Covers card labels and markers for cache contents."""

    def test_format_tag_as_hex_or_dash(self):
        self.assertEqual(format_tag(2), "0x2")
        self.assertEqual(format_tag(None), "-")

    def test_empty_invalid_line_display(self):
        snapshot = [[CacheLineViewModel(0, 0, False, None, False, 0, 0)]]
        card = build_cache_line_card_models(
            snapshot,
            mapped_set=None,
            hit_way=None,
            victim_way=None,
            replacement_reason=None,
        )[0][0]

        self.assertIn("EMPTY", card.markers)
        self.assertEqual(card.tag_text, "-")
        self.assertEqual(card.last_used_text, "-")
        self.assertEqual(card.insert_time_text, "-")
        self.assertEqual(card.style_role, "empty")

    def test_current_set_marker(self):
        snapshot = [[CacheLineViewModel(0, 0, True, 1, False, 4, 2)]]
        card = build_cache_line_card_models(
            snapshot,
            mapped_set=0,
            hit_way=None,
            victim_way=None,
            replacement_reason=None,
        )[0][0]

        self.assertIn("CURRENT SET", card.markers)
        self.assertEqual(card.style_role, "current_set")

    def test_hit_way_marker_has_priority(self):
        snapshot = [[CacheLineViewModel(0, 0, True, 1, False, 4, 2)]]
        card = build_cache_line_card_models(
            snapshot,
            mapped_set=0,
            hit_way=0,
            victim_way=None,
            replacement_reason=None,
        )[0][0]

        self.assertIn("HIT", card.markers)
        self.assertEqual(card.style_role, "hit")

    def test_victim_way_marker(self):
        snapshot = [[CacheLineViewModel(0, 0, True, 1, False, 4, 2)]]
        card = build_cache_line_card_models(
            snapshot,
            mapped_set=0,
            hit_way=None,
            victim_way=0,
            replacement_reason="LRU",
        )[0][0]

        self.assertIn("VICTIM", card.markers)
        self.assertEqual(card.style_role, "victim")

    def test_invalid_fill_marker(self):
        snapshot = [[CacheLineViewModel(0, 0, True, 2, False, 5, 5)]]
        card = build_cache_line_card_models(
            snapshot,
            mapped_set=0,
            hit_way=None,
            victim_way=0,
            replacement_reason="invalid-line",
        )[0][0]

        self.assertIn("INVALID FILL", card.markers)
        self.assertEqual(card.style_role, "invalid_fill")

    def test_direct_mapped_shape(self):
        snapshot = [
            [CacheLineViewModel(0, 0, True, 0, False, 1, 1)],
            [CacheLineViewModel(1, 0, False, None, False, 0, 0)],
        ]
        rows = build_cache_line_card_models(
            snapshot,
            mapped_set=1,
            hit_way=None,
            victim_way=0,
            replacement_reason="invalid-line",
        )

        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(row) == 1 for row in rows))
        self.assertIn("INVALID FILL", rows[1][0].markers)

    def test_four_way_shape(self):
        snapshot = [
            [
                CacheLineViewModel(0, way, True, way, False, way + 1, way + 1)
                for way in range(4)
            ]
        ]
        rows = build_cache_line_card_models(
            snapshot,
            mapped_set=0,
            hit_way=2,
            victim_way=None,
            replacement_reason=None,
        )

        self.assertEqual(len(rows[0]), 4)
        self.assertIn("HIT", rows[0][2].markers)


if __name__ == "__main__":
    unittest.main()
