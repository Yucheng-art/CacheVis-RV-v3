"""Tests for structured Address Visualizer explanations."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from explanation_sections import build_explanation_sections
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


class ExplanationSectionsTest(unittest.TestCase):
    def test_hit_step_has_lookup_and_no_replacement_sections(self):
        sections = build_explanation_sections(
            _step(
                hit=True,
                hit_way=1,
                victim_way=None,
                replacement_reason=None,
                miss_type=None,
                total_accesses=2,
                hits=1,
                misses=1,
                hit_rate=0.5,
                miss_rate=0.5,
            )
        )

        text = "\n".join(line for section in sections for line in section.lines)
        self.assertEqual([section.title for section in sections][1], "Lookup")
        self.assertIn("valid=1 and a matching tag", text)
        self.assertIn("no cache line is filled or replaced", text)
        self.assertIn("Miss type is not applicable", text)

    def test_miss_with_invalid_fill_explains_invalid_line_priority(self):
        sections = build_explanation_sections(_step(victim_way=1))

        text = "\n".join(line for section in sections for line in section.lines)
        self.assertIn("cache miss", text)
        self.assertIn("Way 1 is invalid", text)
        self.assertIn("Invalid lines are preferred", text)

    def test_replacement_explains_policy_victim_and_replaced_tag(self):
        sections = build_explanation_sections(
            _step(
                victim_way=0,
                replaced_valid=True,
                replaced_tag=2,
                replacement_reason="LRU",
                miss_type="unknown",
            )
        )

        text = "\n".join(line for section in sections for line in section.lines)
        self.assertIn("LRU selected way 0", text)
        self.assertIn("tag 0x2", text)

    def test_compulsory_miss_is_identified(self):
        sections = build_explanation_sections(_step(miss_type="compulsory"))

        text = "\n".join(line for section in sections for line in section.lines)
        self.assertIn("Miss type: compulsory", text)
        self.assertIn("first time", text)

    def test_unknown_miss_type_is_reserved_for_later(self):
        sections = build_explanation_sections(_step(miss_type="unknown"))

        text = "\n".join(line for section in sections for line in section.lines)
        self.assertIn("Miss type: unknown", text)
        self.assertIn("reserved for a later milestone", text)


if __name__ == "__main__":
    unittest.main()
