"""Immutable teaching presets for primary locality evidence."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .model import LocalityKind


@dataclass(frozen=True)
class LocalityPreset:
    """One deterministic trace with expected locality and teaching intent."""

    preset_id: str
    title: str
    description: str
    config: CacheConfig
    addresses: tuple[int, ...]
    expected_locality: tuple[LocalityKind, ...]
    expected_teaching_conclusion: str
    expected_hits: int | None = None
    expected_misses: int | None = None


def _config(cache_size: int) -> CacheConfig:
    return CacheConfig(
        cache_size_bytes=cache_size,
        block_size_bytes=16,
        ways=1,
        replacement_policy="LRU",
    )


FIRST = LocalityKind.FIRST_TOUCH
SPATIAL = LocalityKind.SPATIAL
TEMPORAL = LocalityKind.TEMPORAL

SEQUENTIAL_SPATIAL = LocalityPreset(
    preset_id="sequential_spatial",
    title="Sequential Spatial",
    description="Walk through two blocks using adjacent 4-byte elements.",
    config=_config(64),
    addresses=(0, 4, 8, 12, 16, 20, 24, 28),
    expected_locality=(FIRST, SPATIAL, SPATIAL, SPATIAL) * 2,
    expected_teaching_conclusion=(
        "Sequential access exposes spatial locality and lets each fetched block "
        "serve three later addresses."
    ),
    expected_hits=6,
    expected_misses=2,
)

FIXED_STRIDE = LocalityPreset(
    preset_id="fixed_stride",
    title="Fixed Stride",
    description="Use a 16-byte stride so every access enters a new block.",
    config=_config(64),
    addresses=(0, 16, 32, 48, 64, 80, 96, 112),
    expected_locality=(FIRST,) * 8,
    expected_teaching_conclusion=(
        "A block-sized stride skips the remaining offsets in every fetched block."
    ),
    expected_hits=0,
    expected_misses=8,
)

LOOP_TEMPORAL_REUSE = LocalityPreset(
    preset_id="loop_temporal_reuse",
    title="Loop Temporal Reuse",
    description="Repeat the same four addresses after one sequential pass.",
    config=_config(64),
    addresses=(0, 4, 8, 12, 0, 4, 8, 12),
    expected_locality=(FIRST, SPATIAL, SPATIAL, SPATIAL)
    + (TEMPORAL,) * 4,
    expected_teaching_conclusion=(
        "The first pass provides spatial evidence; the repeated exact addresses "
        "provide temporal evidence."
    ),
    expected_hits=7,
    expected_misses=1,
)

BLOCK_LOCALITY = LocalityPreset(
    preset_id="block_locality",
    title="Block Locality",
    description="Mix new and repeated addresses within one 16-byte block.",
    config=_config(32),
    addresses=(0, 4, 8, 12, 8, 4, 12, 0),
    expected_locality=(FIRST, SPATIAL, SPATIAL, SPATIAL)
    + (TEMPORAL,) * 4,
    expected_teaching_conclusion=(
        "One resident block supports both spatial discovery and exact-address reuse."
    ),
    expected_hits=7,
    expected_misses=1,
)

MATRIX_ROW_MAJOR = LocalityPreset(
    preset_id="matrix_row_major",
    title="Matrix Row-Major",
    description="Traverse a 4x4 matrix in contiguous row-major order.",
    config=_config(32),
    addresses=(0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60),
    expected_locality=(FIRST, SPATIAL, SPATIAL, SPATIAL) * 4,
    expected_teaching_conclusion=(
        "Contiguous order realizes spatial locality as twelve cache hits."
    ),
    expected_hits=12,
    expected_misses=4,
)

MATRIX_COLUMN_MAJOR = LocalityPreset(
    preset_id="matrix_column_major",
    title="Matrix Column-Major",
    description="Traverse the same 4x4 row-major layout by columns.",
    config=_config(32),
    addresses=(0, 16, 32, 48, 4, 20, 36, 52, 8, 24, 40, 56, 12, 28, 44, 60),
    expected_locality=(FIRST,) * 4 + (SPATIAL,) * 12,
    expected_teaching_conclusion=(
        "Spatial locality potential still exists, but access order and direct "
        "mapping prevent the cache from using it effectively."
    ),
    expected_hits=0,
    expected_misses=16,
)

LOCALITY_PRESETS = (
    SEQUENTIAL_SPATIAL,
    FIXED_STRIDE,
    LOOP_TEMPORAL_REUSE,
    BLOCK_LOCALITY,
    MATRIX_ROW_MAJOR,
    MATRIX_COLUMN_MAJOR,
)


__all__ = [
    "LocalityPreset",
    "SEQUENTIAL_SPATIAL",
    "FIXED_STRIDE",
    "LOOP_TEMPORAL_REUSE",
    "BLOCK_LOCALITY",
    "MATRIX_ROW_MAJOR",
    "MATRIX_COLUMN_MAJOR",
    "LOCALITY_PRESETS",
]
