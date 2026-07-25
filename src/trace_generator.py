"""Trace generators for simple cache experiments."""

import random
from typing import List, Optional


def generate_sequential_trace(start_address: int, count: int, step: int = 4) -> List[int]:
    """Generate addresses that increase by a fixed step."""
    _validate_count(count)
    _validate_positive_int("step", step)
    return [start_address + i * step for i in range(count)]


def generate_stride_trace(
    start_address: int, count: int, stride_bytes: int
) -> List[int]:
    """Generate addresses that increase by a fixed byte stride."""
    _validate_count(count)
    _validate_positive_int("stride_bytes", stride_bytes)
    return [start_address + i * stride_bytes for i in range(count)]


def generate_random_trace(
    start_address: int,
    count: int,
    address_range_bytes: int,
    alignment: int = 4,
    seed: Optional[int] = None,
) -> List[int]:
    """Generate aligned random addresses within a byte range."""
    _validate_count(count)
    _validate_positive_int("address_range_bytes", address_range_bytes)
    _validate_positive_int("alignment", alignment)

    slots = address_range_bytes // alignment
    if slots <= 0:
        raise ValueError("address_range_bytes must include at least one aligned slot")

    rng = random.Random(seed)
    return [start_address + rng.randrange(slots) * alignment for _ in range(count)]


def generate_matrix_like_trace(
    base_address: int, n: int, element_size: int = 4
) -> List[int]:
    """Generate row-major addresses for an n by n matrix."""
    return generate_matrix_row_major_trace(base_address, n, element_size)


def generate_conflict_trace(
    start_address: int,
    count: int,
    conflict_stride_bytes: int = 4096,
    unique_blocks: int = 4,
) -> List[int]:
    """Generate addresses separated by a cache-sized stride to force conflicts."""
    _validate_count(count)
    _validate_positive_int("conflict_stride_bytes", conflict_stride_bytes)
    _validate_positive_int("unique_blocks", unique_blocks)
    return [
        start_address + (i % unique_blocks) * conflict_stride_bytes
        for i in range(count)
    ]


def generate_loop_reuse_trace(
    start_address: int,
    count: int,
    loop_size: int = 4,
    step: int = 4,
) -> List[int]:
    """Generate repeated accesses to a small working set for temporal locality."""
    _validate_count(count)
    _validate_positive_int("loop_size", loop_size)
    _validate_positive_int("step", step)
    return [start_address + (i % loop_size) * step for i in range(count)]


def generate_block_locality_trace(
    start_address: int,
    count: int,
    block_size_bytes: int = 32,
    word_size: int = 4,
) -> List[int]:
    """Generate word accesses within each block before moving to the next block."""
    _validate_count(count)
    _validate_positive_int("block_size_bytes", block_size_bytes)
    _validate_positive_int("word_size", word_size)
    if block_size_bytes % word_size != 0:
        raise ValueError("block_size_bytes must be divisible by word_size")
    if word_size > block_size_bytes:
        raise ValueError("word_size must not exceed block_size_bytes")
    words_per_block = block_size_bytes // word_size
    return [
        start_address
        + (i // words_per_block) * block_size_bytes
        + (i % words_per_block) * word_size
        for i in range(count)
    ]


def generate_matrix_row_major_trace(
    base_address: int, n: int, element_size: int = 4
) -> List[int]:
    """Generate row-major addresses for an n by n matrix."""
    _validate_count(n)
    _validate_positive_int("element_size", element_size)
    return [
        base_address + (row * n + col) * element_size
        for row in range(n)
        for col in range(n)
    ]


def generate_matrix_column_like_trace(
    base_address: int, n: int, element_size: int = 4
) -> List[int]:
    """Generate column-wise addresses for an n by n row-major matrix."""
    _validate_count(n)
    _validate_positive_int("element_size", element_size)
    return [
        base_address + (row * n + col) * element_size
        for col in range(n)
        for row in range(n)
    ]


def _validate_count(count: int) -> None:
    if not isinstance(count, int) or count < 0:
        raise ValueError("count must be a non-negative integer")


def _validate_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
