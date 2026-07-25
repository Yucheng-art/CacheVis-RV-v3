"""Public pure-Python API for cache-oriented locality analysis."""

from .analyzer import LocalityAnalyzer
from .model import (
    LocalityEvidence,
    LocalityKind,
    LocalityStatistics,
    LocalityStep,
)
from .presets import (
    BLOCK_LOCALITY,
    FIXED_STRIDE,
    LOCALITY_PRESETS,
    LOOP_TEMPORAL_REUSE,
    MATRIX_COLUMN_MAJOR,
    MATRIX_ROW_MAJOR,
    SEQUENTIAL_SPATIAL,
    LocalityPreset,
)
from .session import LocalitySession

__all__ = [
    "LocalityKind",
    "LocalityEvidence",
    "LocalityStatistics",
    "LocalityStep",
    "LocalityAnalyzer",
    "LocalitySession",
    "LocalityPreset",
    "SEQUENTIAL_SPATIAL",
    "FIXED_STRIDE",
    "LOOP_TEMPORAL_REUSE",
    "BLOCK_LOCALITY",
    "MATRIX_ROW_MAJOR",
    "MATRIX_COLUMN_MAJOR",
    "LOCALITY_PRESETS",
]
