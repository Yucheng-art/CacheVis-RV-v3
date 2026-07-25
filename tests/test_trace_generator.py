"""Tests for trace generator helpers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from trace_generator import generate_sequential_trace, generate_stride_trace


class TraceGeneratorTest(unittest.TestCase):
    """Covers deterministic address trace helpers."""

    def test_generate_sequential_trace(self):
        self.assertEqual(
            generate_sequential_trace(0x1000, 4, step=4),
            [0x1000, 0x1004, 0x1008, 0x100C],
        )

    def test_generate_stride_trace(self):
        self.assertEqual(
            generate_stride_trace(0x2000, 4, stride_bytes=16),
            [0x2000, 0x2010, 0x2020, 0x2030],
        )


if __name__ == "__main__":
    unittest.main()
