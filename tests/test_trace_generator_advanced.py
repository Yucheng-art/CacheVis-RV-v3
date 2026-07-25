"""Tests for advanced teaching trace generators."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from trace_generator import (
    generate_block_locality_trace,
    generate_conflict_trace,
    generate_loop_reuse_trace,
    generate_matrix_column_like_trace,
    generate_matrix_row_major_trace,
)


class AdvancedTraceGeneratorTest(unittest.TestCase):
    """Covers address patterns used for teaching cache locality."""

    def test_conflict_trace_repeats_same_set_stride(self):
        trace = generate_conflict_trace(0x1000, 5, conflict_stride_bytes=0x1000)
        self.assertEqual(trace, [0x1000, 0x2000, 0x3000, 0x4000, 0x1000])

    def test_loop_reuse_trace_repeats_small_working_set(self):
        trace = generate_loop_reuse_trace(0x1000, 6, loop_size=3, step=4)
        self.assertEqual(trace, [0x1000, 0x1004, 0x1008, 0x1000, 0x1004, 0x1008])

    def test_block_locality_trace_stays_inside_block_then_moves(self):
        trace = generate_block_locality_trace(0x1000, 10, block_size_bytes=32)
        self.assertEqual(trace[:8], [0x1000 + i * 4 for i in range(8)])
        self.assertEqual(trace[8:], [0x1020, 0x1024])

    def test_block_locality_rejects_misaligned_word_size(self):
        with self.assertRaisesRegex(ValueError, "divisible by word_size"):
            generate_block_locality_trace(0x1000, 4, block_size_bytes=32, word_size=6)

    def test_matrix_row_major_trace(self):
        self.assertEqual(
            generate_matrix_row_major_trace(0x1000, 2, element_size=4),
            [0x1000, 0x1004, 0x1008, 0x100C],
        )

    def test_matrix_column_like_trace(self):
        self.assertEqual(
            generate_matrix_column_like_trace(0x1000, 2, element_size=4),
            [0x1000, 0x1008, 0x1004, 0x100C],
        )


if __name__ == "__main__":
    unittest.main()
