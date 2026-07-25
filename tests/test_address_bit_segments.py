"""Tests for pure Tag / Index / Offset bit segment helpers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from address_bit_segments import split_address_bit_segments


class AddressBitSegmentsTest(unittest.TestCase):
    """Covers binary splitting and bit range labels."""

    def test_splits_normal_32_bit_address(self):
        address_binary = format(0x4C, "032b")
        segments = split_address_bit_segments(
            address_binary,
            tag_bits=26,
            index_bits=2,
            offset_bits=4,
            tag=1,
            index=0,
            offset=0xC,
        )

        self.assertEqual([segment.name for segment in segments], ["Tag", "Index", "Offset"])
        self.assertEqual([segment.bit_count for segment in segments], [26, 2, 4])
        self.assertEqual(segments[0].bits, address_binary[:26])
        self.assertEqual(segments[1].bits, address_binary[26:28])
        self.assertEqual(segments[2].bits, address_binary[28:])
        self.assertEqual("".join(segment.bits for segment in segments), address_binary)

    def test_index_bits_zero_segment_is_explicit(self):
        address_binary = format(0x20, "032b")
        segments = split_address_bit_segments(
            address_binary,
            tag_bits=27,
            index_bits=0,
            offset_bits=5,
            tag=1,
            index=0,
            offset=0,
        )

        self.assertEqual(segments[1].bits, "")
        self.assertEqual(segments[1].bit_count, 0)
        self.assertEqual(segments[1].range_label, "Index: none (0 bits)")
        self.assertEqual("".join(segment.bits for segment in segments), address_binary)

    def test_offset_bits_zero_segment_is_explicit(self):
        address_binary = format(0x03, "032b")
        segments = split_address_bit_segments(
            address_binary,
            tag_bits=30,
            index_bits=2,
            offset_bits=0,
            tag=0,
            index=3,
            offset=0,
        )

        self.assertEqual(segments[2].bits, "")
        self.assertEqual(segments[2].bit_count, 0)
        self.assertEqual(segments[2].range_label, "Offset: none (0 bits)")
        self.assertEqual("".join(segment.bits for segment in segments), address_binary)

    def test_bit_range_labels_are_correct(self):
        segments = split_address_bit_segments(
            "0" * 32,
            tag_bits=20,
            index_bits=7,
            offset_bits=5,
            tag=0,
            index=0,
            offset=0,
        )

        self.assertEqual(segments[0].range_label, "Tag: bits [31:12]")
        self.assertEqual(segments[1].range_label, "Index: bits [11:5]")
        self.assertEqual(segments[2].range_label, "Offset: bits [4:0]")

    def test_rejects_mismatched_bit_counts(self):
        with self.assertRaisesRegex(ValueError, "must equal address length"):
            split_address_bit_segments("0" * 32, 20, 8, 5, 0, 0, 0)


if __name__ == "__main__":
    unittest.main()
