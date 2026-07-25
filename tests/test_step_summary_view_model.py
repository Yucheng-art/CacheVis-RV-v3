"""Tests for selected timeline step summary display models."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from step_summary_view_model import SUMMARY_ONLY_NOTE, build_step_summary
from visualizer_model import AccessStepViewModel


def _step(**overrides):
    values = {
        "step_index": 0,
        "address": 0,
        "address_dec": "0",
        "address_hex": "0x00000000",
        "address_binary": "0" * 32,
        "tag_bits": 30,
        "index_bits": 1,
        "offset_bits": 1,
        "tag": 0,
        "index": 0,
        "offset": 0,
        "mapped_set": 0,
        "hit": False,
        "hit_way": None,
        "victim_way": 1,
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


class StepSummaryViewModelTest(unittest.TestCase):
    def test_hit_summary_includes_hit_way_and_rate_format(self):
        summary = build_step_summary(
            _step(
                step_index=2,
                address_dec="4",
                address_hex="0x00000004",
                hit=True,
                hit_way=0,
                victim_way=None,
                replacement_reason=None,
                miss_type=None,
                hits=1,
                misses=2,
                hit_rate=1 / 3,
                miss_rate=2 / 3,
            )
        )

        text = "\n".join(summary.summary_lines)
        self.assertEqual(summary.result, "HIT")
        self.assertEqual(summary.hit_way, "0")
        self.assertEqual(summary.hit_rate, "33.33%")
        self.assertIn("Step 2 selected.", text)
        self.assertIn("Reason: valid bit is 1 and tag matches.", text)
        self.assertIn(SUMMARY_ONLY_NOTE, text)

    def test_compulsory_invalid_fill_summary(self):
        summary = build_step_summary(_step(victim_way=1, miss_type="compulsory"))

        text = "\n".join(summary.summary_lines)
        self.assertEqual(summary.result, "MISS")
        self.assertEqual(summary.miss_type, "compulsory")
        self.assertEqual(summary.victim_way, "1")
        self.assertEqual(summary.replaced_tag, "-")
        self.assertIn("Fill: invalid line is filled first.", text)
        self.assertIn("Rates: hit 0.00%, miss 100.00%.", text)

    def test_victim_replacement_summary_formats_replaced_tag(self):
        summary = build_step_summary(
            _step(
                victim_way=0,
                replaced_valid=True,
                replaced_tag=3,
                replacement_reason="LRU",
                miss_type="unknown",
            )
        )

        text = "\n".join(summary.summary_lines)
        self.assertEqual(summary.replaced_tag, "0x3")
        self.assertIn("Replacement: LRU selected the victim way.", text)
        self.assertIn("conflict/capacity classification is reserved", text)

    def test_unknown_miss_type_is_preserved(self):
        summary = build_step_summary(_step(miss_type="unknown"))

        self.assertEqual(summary.miss_type, "unknown")
        self.assertIn("Miss type: unknown", "\n".join(summary.summary_lines))


if __name__ == "__main__":
    unittest.main()
