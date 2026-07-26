"""Strict read/write trace parser tests."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cachevis_rv.labs.write_policy import MemoryAccessKind, parse_memory_access_trace


class WritePolicyParserTest(unittest.TestCase):
    def test_decimal_hex_newline_comma_colon_and_case(self):
        parsed = parse_memory_access_trace("r 0\nW:0x10, R 24\nw:32")
        self.assertEqual(
            tuple((item.kind, item.address) for item in parsed),
            ((MemoryAccessKind.READ, 0), (MemoryAccessKind.WRITE, 16),
             (MemoryAccessKind.READ, 24), (MemoryAccessKind.WRITE, 32)),
        )

    def test_empty_text_is_an_empty_trace(self):
        self.assertEqual(parse_memory_access_trace(" \n "), ())

    def test_bare_address_and_unknown_operation_are_rejected(self):
        for text in ("16", "X 0"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "unknown"):
                parse_memory_access_trace(text)

    def test_missing_invalid_negative_and_extra_address_fields_are_rejected(self):
        cases = ("R", "R:", "W nope", "R -1", "R 0 extra")
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_memory_access_trace(text)

    def test_obvious_empty_comma_item_is_rejected(self):
        for text in ("R 0,,W 4", ",R 0", "R 0,"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "empty item"):
                parse_memory_access_trace(text)


if __name__ == "__main__":
    unittest.main()
