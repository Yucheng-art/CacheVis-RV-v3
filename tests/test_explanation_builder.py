"""Tests for visualizer explanation text generation."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_config import CacheConfig
from explanation_builder import build_explanation_lines
from visualizer_model import CacheLineViewModel


class ExplanationBuilderTest(unittest.TestCase):
    """Covers hit, miss, invalid fill, and replacement explanations."""

    def setUp(self):
        self.config = CacheConfig(cache_size_bytes=64, block_size_bytes=16, ways=1)

    def test_hit_explanation_mentions_valid_and_matching_tag(self):
        lines = build_explanation_lines(
            self.config,
            address=0x04,
            tag=0,
            index=0,
            offset=4,
            hit=True,
            hit_way=0,
            victim_way=None,
            replaced_valid=False,
            replaced_tag=None,
            replacement_reason=None,
            miss_type=None,
            before_set_lines=[
                CacheLineViewModel(0, 0, True, 0, False, 1, 1),
            ],
        )

        text = "\n".join(lines)
        self.assertIn("valid=1 and matching tag=0", text)
        self.assertIn("cache hit", text)

    def test_miss_explanation_mentions_invalid_line_and_compulsory(self):
        lines = build_explanation_lines(
            self.config,
            address=0x00,
            tag=0,
            index=0,
            offset=0,
            hit=False,
            hit_way=None,
            victim_way=0,
            replaced_valid=False,
            replaced_tag=None,
            replacement_reason="invalid-line",
            miss_type="compulsory",
            before_set_lines=[
                CacheLineViewModel(0, 0, False, None, False, 0, 0),
            ],
        )

        text = "\n".join(lines)
        self.assertIn("cache miss", text)
        self.assertIn("compulsory", text)
        self.assertIn("invalid", text)

    def test_replacement_explanation_mentions_policy_and_replaced_tag(self):
        lines = build_explanation_lines(
            self.config,
            address=0x40,
            tag=1,
            index=0,
            offset=0,
            hit=False,
            hit_way=None,
            victim_way=0,
            replaced_valid=True,
            replaced_tag=0,
            replacement_reason="LRU",
            miss_type="unknown",
            before_set_lines=[
                CacheLineViewModel(0, 0, True, 0, False, 1, 1),
            ],
        )

        text = "\n".join(lines)
        self.assertIn("LRU selects way 0", text)
        self.assertIn("replaced tag is 0", text)


if __name__ == "__main__":
    unittest.main()
