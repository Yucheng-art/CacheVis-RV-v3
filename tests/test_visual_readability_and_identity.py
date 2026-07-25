"""Regression tests for V3 identity and light semantic surface readability."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.address_explorer.view_models.timeline import TimelineItemViewModel
from cachevis_rv.labs.address_explorer.widgets.address_bit_bar import (
    SEGMENT_STYLES,
    SEGMENT_TEXT_COLORS,
)
from cachevis_rv.labs.address_explorer.widgets.cache_contents import (
    CARD_STYLES,
    CARD_TEXT_COLORS,
    _card_style,
    _row_style,
)
from cachevis_rv.labs.address_explorer.widgets.explanation_panel import (
    SECTION_STYLES,
    SECTION_TEXT_COLORS,
    _section_style,
)
from cachevis_rv.labs.address_explorer.widgets.timeline import (
    CHIP_STYLES,
    CHIP_TEXT_COLORS,
    _chip_style,
)
from version import APP_NAME, APP_VERSION


class VisualReadabilityAndIdentityTest(unittest.TestCase):
    def test_application_identity_is_v3(self):
        self.assertEqual(APP_NAME, "CacheVis-RV")
        self.assertEqual(APP_VERSION, "V3.0")
        self.assertNotIn("V1.0", f"{APP_NAME} {APP_VERSION}")

    def test_segment_light_surfaces_have_dark_semantic_text(self):
        self.assertEqual(set(SEGMENT_STYLES), set(SEGMENT_TEXT_COLORS))
        self.assertEqual(SEGMENT_TEXT_COLORS["Tag"], "#6b1f1f")
        self.assertEqual(SEGMENT_TEXT_COLORS["Index"], "#14532d")
        self.assertEqual(SEGMENT_TEXT_COLORS["Offset"], "#173f73")

    def test_cache_cards_have_explicit_dark_text(self):
        self.assertEqual(set(CARD_STYLES), set(CARD_TEXT_COLORS))
        for role, color in CARD_TEXT_COLORS.items():
            with self.subTest(role=role):
                self.assertIn(f"color: {color}", _card_style(role))

    def test_cache_rows_have_explicit_dark_text(self):
        self.assertIn("color: #173f73", _row_style(True))
        self.assertIn("color: #1f2937", _row_style(False))

    def test_explanation_sections_have_explicit_dark_text(self):
        self.assertEqual(set(SECTION_STYLES), set(SECTION_TEXT_COLORS))
        for status, color in SECTION_TEXT_COLORS.items():
            with self.subTest(status=status):
                self.assertIn(f"color: {color}", _section_style(status))

    def test_timeline_chips_have_explicit_dark_text(self):
        self.assertEqual(set(CHIP_STYLES), set(CHIP_TEXT_COLORS))
        for result in ("HIT", "MISS"):
            for is_current, is_selected in (
                (False, False),
                (True, False),
                (False, True),
                (True, True),
            ):
                item = TimelineItemViewModel(
                    step_index=0,
                    address_dec="0",
                    address_hex="0x00000000",
                    result=result,
                    miss_type="-" if result == "HIT" else "compulsory",
                    mapped_set=0,
                    hit_way=0 if result == "HIT" else None,
                    victim_way=None if result == "HIT" else 0,
                    label=f"Step 1\n0x0\n{result}",
                    tooltip_lines=[],
                    is_current=is_current,
                    is_selected=is_selected,
                )
                with self.subTest(
                    result=result,
                    is_current=is_current,
                    is_selected=is_selected,
                ):
                    self.assertIn("color: #", _chip_style(item))


if __name__ == "__main__":
    unittest.main()
