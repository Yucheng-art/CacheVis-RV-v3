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
from .block_access_view_model import (
    BlockAccessCellViewModel,
    BlockAccessSummaryViewModel,
    build_block_access_models,
)
from .cache_view_model import (
    LocalityCacheLineViewModel,
    build_cache_line_models,
)
from .controller import LocalityController
from .evidence_view_model import (
    LocalityEvidenceViewModel,
    build_evidence_view_model,
)
from .page_state import EMPTY_PAGE_STATE, LocalityPageState
from .statistics_view_model import (
    LocalityStatisticsViewModel,
    build_statistics_view_model,
)
from .timeline_view_model import (
    LocalityTimelineItemViewModel,
    build_timeline_item,
    build_timeline_items,
)

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
    "LocalityController",
    "LocalityPageState",
    "EMPTY_PAGE_STATE",
    "LocalityCacheLineViewModel",
    "build_cache_line_models",
    "LocalityEvidenceViewModel",
    "build_evidence_view_model",
    "LocalityStatisticsViewModel",
    "build_statistics_view_model",
    "LocalityTimelineItemViewModel",
    "build_timeline_item",
    "build_timeline_items",
    "BlockAccessCellViewModel",
    "BlockAccessSummaryViewModel",
    "build_block_access_models",
]
