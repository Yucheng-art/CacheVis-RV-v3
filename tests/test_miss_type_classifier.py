"""Unit tests for the pure strict-3C classifier."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.miss_type import MissType, MissTypeClassifier


class MissTypeClassifierTest(unittest.TestCase):
    def setUp(self):
        self.classifier = MissTypeClassifier()

    def test_first_block_miss_is_compulsory(self):
        miss_type, evidence = self.classifier.classify(
            7,
            actual_hit=False,
            reference_hit=False,
        )

        self.assertIs(miss_type, MissType.COMPULSORY)
        self.assertFalse(evidence.seen_before)
        self.assertTrue(evidence.actual_miss)
        self.assertTrue(evidence.reference_miss)

    def test_same_block_offset_is_not_a_new_compulsory_block(self):
        self.classifier.classify(2, actual_hit=False, reference_hit=False)
        miss_type, evidence = self.classifier.classify(
            2,
            actual_hit=True,
            reference_hit=True,
        )

        self.assertIsNone(miss_type)
        self.assertTrue(evidence.seen_before)
        self.assertEqual(self.classifier.seen_blocks, frozenset({2}))

    def test_actual_hit_has_no_miss_type(self):
        self.classifier.classify(1, actual_hit=False, reference_hit=False)
        miss_type, evidence = self.classifier.classify(
            1,
            actual_hit=True,
            reference_hit=False,
        )

        self.assertIsNone(miss_type)
        self.assertTrue(evidence.actual_hit)
        self.assertIn("do not have a miss type", evidence.classification_reason)

    def test_repeated_actual_miss_reference_hit_is_conflict(self):
        self.classifier.classify(0, actual_hit=False, reference_hit=False)
        miss_type, evidence = self.classifier.classify(
            0,
            actual_hit=False,
            reference_hit=True,
        )

        self.assertIs(miss_type, MissType.CONFLICT)
        self.assertTrue(evidence.seen_before)
        self.assertTrue(evidence.reference_hit)

    def test_repeated_actual_miss_reference_miss_is_capacity(self):
        self.classifier.classify(0, actual_hit=False, reference_hit=False)
        miss_type, evidence = self.classifier.classify(
            0,
            actual_hit=False,
            reference_hit=False,
        )

        self.assertIs(miss_type, MissType.CAPACITY)
        self.assertTrue(evidence.seen_before)
        self.assertTrue(evidence.reference_miss)

    def test_reset_clears_seen_blocks(self):
        self.classifier.classify(5, actual_hit=False, reference_hit=False)
        self.classifier.reset()

        self.assertEqual(self.classifier.seen_blocks, frozenset())
        miss_type, _ = self.classifier.classify(
            5,
            actual_hit=False,
            reference_hit=False,
        )
        self.assertIs(miss_type, MissType.COMPULSORY)

    def test_self_contradictory_first_access_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "first access"):
            self.classifier.classify(3, actual_hit=True, reference_hit=False)
        with self.assertRaisesRegex(ValueError, "first access"):
            self.classifier.classify(3, actual_hit=False, reference_hit=True)

        self.assertEqual(self.classifier.seen_blocks, frozenset())

    def test_invalid_input_types_are_rejected(self):
        with self.assertRaises(TypeError):
            self.classifier.classify(True, actual_hit=False, reference_hit=False)
        with self.assertRaises(ValueError):
            self.classifier.classify(-1, actual_hit=False, reference_hit=False)
        with self.assertRaises(TypeError):
            self.classifier.classify(0, actual_hit=1, reference_hit=False)


if __name__ == "__main__":
    unittest.main()
