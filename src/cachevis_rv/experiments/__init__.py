"""Public address-trace parsing and generation services."""

from .address_trace_parser import parse_address_trace
from .trace_generator import (
    generate_block_locality_trace,
    generate_conflict_trace,
    generate_loop_reuse_trace,
    generate_matrix_column_like_trace,
    generate_matrix_like_trace,
    generate_matrix_row_major_trace,
    generate_random_trace,
    generate_sequential_trace,
    generate_stride_trace,
)

__all__ = [
    "parse_address_trace",
    "generate_sequential_trace",
    "generate_stride_trace",
    "generate_random_trace",
    "generate_matrix_like_trace",
    "generate_conflict_trace",
    "generate_loop_reuse_trace",
    "generate_block_locality_trace",
    "generate_matrix_row_major_trace",
    "generate_matrix_column_like_trace",
]
