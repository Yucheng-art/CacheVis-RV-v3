"""Tests for replacement policy victim selection."""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cache_line import CacheLine
from replacement_policy import choose_victim_way


class ReplacementPolicyTest(unittest.TestCase):
    """Covers invalid-first behavior and each supported policy."""

    def test_invalid_line_is_selected_first(self):
        lines = [
            CacheLine(valid=True, tag=1),
            CacheLine(valid=False),
            CacheLine(valid=False),
        ]
        self.assertEqual(choose_victim_way(lines, "LRU"), 1)

    def test_lru_selects_smallest_last_used(self):
        lines = [
            CacheLine(valid=True, tag=1, last_used=5),
            CacheLine(valid=True, tag=2, last_used=2),
        ]
        self.assertEqual(choose_victim_way(lines, "LRU"), 1)

    def test_fifo_selects_smallest_insert_time(self):
        lines = [
            CacheLine(valid=True, tag=1, insert_time=5),
            CacheLine(valid=True, tag=2, insert_time=2),
        ]
        self.assertEqual(choose_victim_way(lines, "FIFO"), 1)

    def test_random_uses_supplied_random_source(self):
        lines = [CacheLine(valid=True, tag=1), CacheLine(valid=True, tag=2)]
        self.assertEqual(choose_victim_way(lines, "Random", random.Random(0)), 1)

    def test_unknown_policy_raises(self):
        lines = [CacheLine(valid=True, tag=1)]
        with self.assertRaisesRegex(ValueError, "unsupported replacement policy"):
            choose_victim_way(lines, "Clock")


if __name__ == "__main__":
    unittest.main()
