"""Compatibility tests for the packaged Address Explorer and flat facades."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from address_bit_bar import AddressBitBarWidget as FlatAddressBitBarWidget
from address_bit_segments import (
    AddressBitSegment as FlatAddressBitSegment,
    split_address_bit_segments as flat_split_address_bit_segments,
)
from address_trace_parser import parse_address_trace as flat_parse_address_trace
from cache_contents_view_model import (
    CacheLineCardViewModel as FlatCacheLineCardViewModel,
    build_cache_line_card_model as flat_build_cache_line_card_model,
    build_cache_line_card_models as flat_build_cache_line_card_models,
    format_tag as flat_format_tag,
)
from cache_contents_widget import CacheContentsWidget as FlatCacheContentsWidget
from cachevis_rv.core import CacheConfig
from cachevis_rv.labs.address_explorer.address_bits import (
    AddressBitSegment,
    split_address_bit_segments,
)
from cachevis_rv.labs.address_explorer.engine import VisualizerStepEngine
from cachevis_rv.labs.address_explorer.explanation_builder import (
    build_explanation_lines,
)
from cachevis_rv.labs.address_explorer.model import (
    AccessStepViewModel,
    CacheLineViewModel,
)
from cachevis_rv.labs.address_explorer.parser import parse_address_trace
from cachevis_rv.labs.address_explorer.view_models.cache_contents import (
    CacheLineCardViewModel,
    build_cache_line_card_model,
    build_cache_line_card_models,
    format_tag,
)
from cachevis_rv.labs.address_explorer.view_models.explanation import (
    ExplanationSection,
    build_explanation_sections,
)
from cachevis_rv.labs.address_explorer.view_models.step_summary import (
    SUMMARY_ONLY_NOTE,
    StepSummaryViewModel,
    build_step_summary,
)
from cachevis_rv.labs.address_explorer.view_models.timeline import (
    TimelineItemViewModel,
    build_timeline_item,
)
from cachevis_rv.labs.address_explorer.widget import (
    DEMO_PRESETS,
    AddressVisualizerWidget,
)
from cachevis_rv.labs.address_explorer.widgets.address_bit_bar import (
    AddressBitBarWidget,
)
from cachevis_rv.labs.address_explorer.widgets.cache_contents import (
    CacheContentsWidget,
)
from cachevis_rv.labs.address_explorer.widgets.explanation_panel import (
    ExplanationPanelWidget,
)
from cachevis_rv.labs.address_explorer.widgets.step_summary import StepSummaryWidget
from cachevis_rv.labs.address_explorer.widgets.timeline import AccessTimelineWidget
from explanation_builder import build_explanation_lines as flat_build_explanation_lines
from explanation_panel_widget import (
    ExplanationPanelWidget as FlatExplanationPanelWidget,
)
from explanation_sections import (
    ExplanationSection as FlatExplanationSection,
    build_explanation_sections as flat_build_explanation_sections,
)
from step_summary_view_model import (
    SUMMARY_ONLY_NOTE as FLAT_SUMMARY_ONLY_NOTE,
    StepSummaryViewModel as FlatStepSummaryViewModel,
    build_step_summary as flat_build_step_summary,
)
from step_summary_widget import StepSummaryWidget as FlatStepSummaryWidget
from timeline_view_model import (
    TimelineItemViewModel as FlatTimelineItemViewModel,
    build_timeline_item as flat_build_timeline_item,
)
from timeline_widget import AccessTimelineWidget as FlatAccessTimelineWidget
from visualizer_model import (
    AccessStepViewModel as FlatAccessStepViewModel,
    CacheLineViewModel as FlatCacheLineViewModel,
)
from visualizer_step_engine import VisualizerStepEngine as FlatVisualizerStepEngine
from visualizer_widget import (
    DEMO_PRESETS as FLAT_DEMO_PRESETS,
    AddressVisualizerWidget as FlatAddressVisualizerWidget,
)


class AddressExplorerPackageCompatibilityTest(unittest.TestCase):
    """Proves package extraction preserves Address Visualizer behavior."""

    def test_parser_bit_segments_models_engine_and_explanation_are_same_objects(self):
        self.assertIs(flat_parse_address_trace, parse_address_trace)
        self.assertIs(FlatAddressBitSegment, AddressBitSegment)
        self.assertIs(flat_split_address_bit_segments, split_address_bit_segments)
        self.assertIs(FlatAccessStepViewModel, AccessStepViewModel)
        self.assertIs(FlatCacheLineViewModel, CacheLineViewModel)
        self.assertIs(FlatVisualizerStepEngine, VisualizerStepEngine)
        self.assertIs(flat_build_explanation_lines, build_explanation_lines)

    def test_four_view_model_facades_export_same_objects(self):
        self.assertIs(FlatCacheLineCardViewModel, CacheLineCardViewModel)
        self.assertIs(flat_build_cache_line_card_model, build_cache_line_card_model)
        self.assertIs(flat_build_cache_line_card_models, build_cache_line_card_models)
        self.assertIs(flat_format_tag, format_tag)
        self.assertIs(FlatExplanationSection, ExplanationSection)
        self.assertIs(flat_build_explanation_sections, build_explanation_sections)
        self.assertIs(FlatTimelineItemViewModel, TimelineItemViewModel)
        self.assertIs(flat_build_timeline_item, build_timeline_item)
        self.assertIs(FlatStepSummaryViewModel, StepSummaryViewModel)
        self.assertIs(flat_build_step_summary, build_step_summary)
        self.assertIs(FLAT_SUMMARY_ONLY_NOTE, SUMMARY_ONLY_NOTE)

    def test_widget_facades_export_same_class_objects(self):
        self.assertIs(FlatAddressBitBarWidget, AddressBitBarWidget)
        self.assertIs(FlatCacheContentsWidget, CacheContentsWidget)
        self.assertIs(FlatExplanationPanelWidget, ExplanationPanelWidget)
        self.assertIs(FlatAccessTimelineWidget, AccessTimelineWidget)
        self.assertIs(FlatStepSummaryWidget, StepSummaryWidget)
        self.assertIs(FlatAddressVisualizerWidget, AddressVisualizerWidget)

    def test_demo_presets_preserve_identity_content_and_order(self):
        expected = {
            "Dan-style LRU demo": {
                "addresses": "0 2 0 1 4 0",
                "cache_size": "4",
                "block_size": "1",
                "ways": "2",
                "policy": "LRU",
            },
            "Direct-mapped conflict demo": {
                "addresses": "0 4 0 4",
                "cache_size": "4",
                "block_size": "1",
                "ways": "1",
                "policy": "LRU",
            },
            "Spatial locality demo": {
                "addresses": "0 1 2 3 4 5 6 7",
                "cache_size": "8",
                "block_size": "4",
                "ways": "1",
                "policy": "LRU",
            },
            "Hex address demo": {
                "addresses": "0x14 0x1c 0x34 0x8014",
                "cache_size": "16384",
                "block_size": "16",
                "ways": "1",
                "policy": "LRU",
            },
        }
        self.assertIs(FLAT_DEMO_PRESETS, DEMO_PRESETS)
        self.assertEqual(DEMO_PRESETS, expected)
        self.assertEqual(list(DEMO_PRESETS), list(expected))

    def test_fixed_trace_hit_miss_sequence_is_unchanged(self):
        config = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=2,
            replacement_policy="LRU",
        )
        engine = VisualizerStepEngine(config, [0, 2, 0, 1, 4, 0])

        steps = [engine.step() for _ in range(6)]

        self.assertEqual(
            [step.hit for step in steps],
            [False, False, True, False, False, True],
        )

    def test_miss_types_remain_compulsory_or_unknown(self):
        config = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=1,
            replacement_policy="LRU",
        )
        engine = VisualizerStepEngine(config, [0, 4, 0])

        steps = [engine.step() for _ in range(3)]

        self.assertEqual([step.miss_type for step in steps], [
            "compulsory",
            "compulsory",
            "unknown",
        ])
        self.assertLessEqual(
            {step.miss_type for step in steps if not step.hit},
            {"compulsory", "unknown"},
        )

    def test_timeline_current_and_selected_semantics_are_unchanged(self):
        step = VisualizerStepEngine(
            CacheConfig(cache_size_bytes=4, block_size_bytes=1, ways=2),
            [0],
        ).step()

        item = build_timeline_item(step, is_current=True, is_selected=True)

        self.assertTrue(item.is_current)
        self.assertTrue(item.is_selected)
        self.assertTrue(item.label.startswith("CURRENT | SELECTED | Step 0"))

    def test_step_summary_retains_summary_only_no_rollback_semantics(self):
        step = VisualizerStepEngine(
            CacheConfig(cache_size_bytes=4, block_size_bytes=1, ways=2),
            [0],
        ).step()

        summary = build_step_summary(step)

        self.assertEqual(summary.note, SUMMARY_ONLY_NOTE)
        self.assertIn("step summary only", summary.note.lower())
        self.assertIn("remains at the current/latest state", summary.note.lower())
        self.assertIn(f"Note: {SUMMARY_ONLY_NOTE}", summary.summary_lines)

    def test_zero_bit_index_and_offset_display_are_unchanged(self):
        fully_associative = CacheConfig(
            cache_size_bytes=4,
            block_size_bytes=1,
            ways=4,
        )
        full_step = VisualizerStepEngine(fully_associative, [3]).step()
        full_segments = split_address_bit_segments(
            full_step.address_binary,
            full_step.tag_bits,
            full_step.index_bits,
            full_step.offset_bits,
            full_step.tag,
            full_step.index,
            full_step.offset,
        )

        self.assertEqual(full_step.index_bits, 0)
        self.assertEqual(full_segments[1].bits, "")
        self.assertEqual(full_segments[1].range_label, "Index: none (0 bits)")
        self.assertEqual(full_step.offset_bits, 0)
        self.assertEqual(full_segments[2].bits, "")
        self.assertEqual(full_segments[2].range_label, "Offset: none (0 bits)")

    def test_pure_logic_package_contains_no_pyside6_import(self):
        package_root = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "cachevis_rv"
            / "labs"
            / "address_explorer"
        )
        pure_files = [
            package_root / "parser.py",
            package_root / "address_bits.py",
            package_root / "model.py",
            package_root / "engine.py",
            package_root / "explanation_builder.py",
            *(package_root / "view_models").glob("*.py"),
        ]

        for path in pure_files:
            with self.subTest(path=path.name):
                self.assertNotIn("PySide6", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
