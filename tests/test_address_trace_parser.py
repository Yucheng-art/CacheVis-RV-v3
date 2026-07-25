"""Tests for user-entered address trace parsing."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from address_trace_parser import parse_address_trace


class AddressTraceParserTest(unittest.TestCase):
    """Covers decimal, hex, mixed separators, and clear errors."""

    def test_parse_decimal_addresses(self):
        self.assertEqual(parse_address_trace("0 2 0 1 4 0"), [0, 2, 0, 1, 4, 0])

    def test_parse_hex_addresses(self):
        self.assertEqual(
            parse_address_trace("0x14 0x1c 0x34 0x8014"),
            [0x14, 0x1C, 0x34, 0x8014],
        )

    def test_parse_mixed_separators(self):
        text = "0, 2, 0x14\n0x1c 0x34"
        self.assertEqual(parse_address_trace(text), [0, 2, 0x14, 0x1C, 0x34])

    def test_invalid_token_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "invalid address token: 'oops'"):
            parse_address_trace("0 oops 4")

    def test_empty_input_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            parse_address_trace(" \n\t ")

    def test_negative_address_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "address must be non-negative"):
            parse_address_trace("0 -1 4")


if __name__ == "__main__":
    unittest.main()
