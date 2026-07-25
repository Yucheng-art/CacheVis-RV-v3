"""Compatibility tests for the shared address-trace parser extraction."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from address_trace_parser import parse_address_trace as flat_parse
from cachevis_rv.experiments import parse_address_trace as public_parse
from cachevis_rv.experiments.address_trace_parser import parse_address_trace
from cachevis_rv.labs.address_explorer.parser import (
    parse_address_trace as explorer_parse,
)


class SharedAddressTraceParserTest(unittest.TestCase):
    def test_all_public_paths_share_one_implementation(self):
        self.assertIs(parse_address_trace, public_parse)
        self.assertIs(parse_address_trace, explorer_parse)
        self.assertIs(parse_address_trace, flat_parse)

    def test_decimal_hex_and_mixed_separators(self):
        self.assertEqual(
            parse_address_trace("0, 0x4\n8  0xC"),
            [0, 4, 8, 12],
        )

    def test_empty_invalid_and_negative_input_fail_clearly(self):
        cases = (
            ("", "empty"),
            ("1, nope", "invalid address token"),
            ("1, -2", "non-negative"),
        )
        for text, message in cases:
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, message):
                    parse_address_trace(text)


if __name__ == "__main__":
    unittest.main()
