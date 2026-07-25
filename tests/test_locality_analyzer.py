"""Unit tests for cache-independent primary locality evidence."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.locality import LocalityAnalyzer, LocalityKind


class LocalityAnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.analyzer = LocalityAnalyzer()

    def analyze(self, address, step, block_size=16):
        return self.analyzer.analyze(address, block_size, step)

    def test_first_block_access_is_first_touch(self):
        kind, evidence = self.analyze(20, 0)

        self.assertIs(kind, LocalityKind.FIRST_TOUCH)
        self.assertFalse(evidence.address_seen_before)
        self.assertFalse(evidence.block_seen_before)
        self.assertIsNone(evidence.block_reuse_distance)
        self.assertIn("first touch", evidence.classification_reason)

    def test_new_address_in_seen_block_is_spatial(self):
        self.analyze(16, 0)
        kind, evidence = self.analyze(20, 1)

        self.assertIs(kind, LocalityKind.SPATIAL)
        self.assertFalse(evidence.address_seen_before)
        self.assertTrue(evidence.block_seen_before)
        self.assertFalse(evidence.offset_seen_before)

    def test_repeated_exact_address_is_temporal(self):
        self.analyze(16, 0)
        kind, evidence = self.analyze(16, 1)

        self.assertIs(kind, LocalityKind.TEMPORAL)
        self.assertTrue(evidence.address_seen_before)
        self.assertTrue(evidence.block_seen_before)
        self.assertTrue(evidence.offset_seen_before)

    def test_temporal_has_priority_over_spatial(self):
        self.analyze(0, 0)
        self.analyze(4, 1)
        kind, _evidence = self.analyze(0, 2)

        self.assertIs(kind, LocalityKind.TEMPORAL)

    def test_block_and_offset_use_integer_division_and_modulo(self):
        kind, evidence = self.analyze(23, 0, block_size=8)

        self.assertIs(kind, LocalityKind.FIRST_TOUCH)
        self.assertEqual(self.analyzer.seen_blocks, frozenset({2}))
        self.assertFalse(evidence.offset_seen_before)
        _kind, new_offset = self.analyze(16, 1, block_size=8)
        _kind, repeated_offset = self.analyze(16, 2, block_size=8)
        self.assertFalse(new_offset.offset_seen_before)
        self.assertTrue(repeated_offset.offset_seen_before)

    def test_previous_steps_and_reuse_gaps_are_exact(self):
        self.analyze(0, 0)
        self.analyze(4, 1)
        _kind, evidence = self.analyze(0, 2)

        self.assertEqual(evidence.previous_address_step, 0)
        self.assertEqual(evidence.previous_block_step, 1)
        self.assertEqual(evidence.address_reuse_gap, 2)
        self.assertEqual(evidence.block_reuse_gap, 1)

    def test_same_block_transition_and_address_delta(self):
        _kind, first = self.analyze(8, 0)
        _kind, same = self.analyze(12, 1)
        _kind, other = self.analyze(32, 2)

        self.assertFalse(first.same_block_as_previous)
        self.assertIsNone(first.address_delta)
        self.assertTrue(same.same_block_as_previous)
        self.assertEqual(same.address_delta, 4)
        self.assertFalse(other.same_block_as_previous)
        self.assertEqual(other.address_delta, 20)

    def test_reset_clears_every_public_history(self):
        self.analyze(0, 0)
        self.analyze(4, 1)
        self.analyzer.reset()

        self.assertEqual(self.analyzer.seen_addresses, frozenset())
        self.assertEqual(self.analyzer.seen_blocks, frozenset())
        kind, evidence = self.analyze(0, 0)
        self.assertIs(kind, LocalityKind.FIRST_TOUCH)
        self.assertIsNone(evidence.previous_address_step)

    def test_reuse_distance_a_a_is_zero(self):
        self.analyze(0, 0, 1)
        _kind, evidence = self.analyze(0, 1, 1)

        self.assertEqual(evidence.block_reuse_distance, 0)

    def test_reuse_distance_a_b_a_is_one(self):
        for step, block in enumerate((0, 1)):
            self.analyze(block, step, 1)
        _kind, evidence = self.analyze(0, 2, 1)

        self.assertEqual(evidence.block_reuse_distance, 1)

    def test_reuse_distance_a_b_c_a_is_two(self):
        for step, block in enumerate((0, 1, 2)):
            self.analyze(block, step, 1)
        _kind, evidence = self.analyze(0, 3, 1)

        self.assertEqual(evidence.block_reuse_distance, 2)

    def test_reuse_distance_a_b_a_c_a_is_one(self):
        for step, block in enumerate((0, 1, 0, 2)):
            self.analyze(block, step, 1)
        _kind, evidence = self.analyze(0, 4, 1)

        self.assertEqual(evidence.block_reuse_distance, 1)

    def test_invalid_arguments_are_rejected(self):
        cases = (
            ((-1, 16, 0), "address"),
            ((0, 0, 0), "block_size_bytes"),
            ((0, 16, -1), "step_index"),
        )
        for args, message in cases:
            with self.subTest(args=args):
                with self.assertRaisesRegex(ValueError, message):
                    self.analyzer.analyze(*args)

    def test_step_index_must_increase(self):
        self.analyze(0, 0)

        with self.assertRaisesRegex(ValueError, "increase"):
            self.analyze(4, 0)


if __name__ == "__main__":
    unittest.main()
