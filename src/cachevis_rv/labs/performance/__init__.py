"""Pure-logic public API for performance modeling and sweeps."""

from .hierarchy import (
    TwoLevelPerformanceAnalyzer,
    TwoLevelPerformanceResult,
    TwoLevelTimingModel,
)
from .model import (
    PerformanceCacheLineSnapshot,
    PerformanceCacheSnapshot,
    PerformanceMetrics,
    PerformanceRunResult,
    PerformanceRunSpec,
)
from .presets import (
    ANALYTICAL_L1_L2_EXAMPLE,
    ANALYTICAL_L1_L2_MODEL,
    ASSOCIATIVITY_CONFLICT_RELIEF,
    ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP,
    CAPACITY_KNEE,
    CAPACITY_KNEE_SWEEP,
    HIT_RATE_IS_NOT_AMAT,
    HIT_RATE_IS_NOT_AMAT_SWEEP,
    MISS_PENALTY_SENSITIVITY,
    MISS_PENALTY_SENSITIVITY_SWEEP,
    PERFORMANCE_PRESETS,
    PERFORMANCE_SWEEP_PRESETS,
    PerformancePreset,
    SEQUENTIAL_BLOCK_BENEFIT,
    SEQUENTIAL_BLOCK_BENEFIT_SWEEP,
    STRIDE_BLOCK_COST,
    STRIDE_BLOCK_COST_SWEEP,
)
from .runner import PerformanceRunner
from .sweep import (
    PerformanceSweepDefinition,
    PerformanceSweepKind,
    PerformanceSweepPointResult,
    PerformanceSweepResult,
    PerformanceSweepRunner,
)
from .timing import PerformanceTimingModel

__all__ = [
    "ANALYTICAL_L1_L2_EXAMPLE",
    "ANALYTICAL_L1_L2_MODEL",
    "ASSOCIATIVITY_CONFLICT_RELIEF",
    "ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP",
    "CAPACITY_KNEE",
    "CAPACITY_KNEE_SWEEP",
    "HIT_RATE_IS_NOT_AMAT",
    "HIT_RATE_IS_NOT_AMAT_SWEEP",
    "MISS_PENALTY_SENSITIVITY",
    "MISS_PENALTY_SENSITIVITY_SWEEP",
    "PERFORMANCE_PRESETS",
    "PERFORMANCE_SWEEP_PRESETS",
    "PerformanceCacheLineSnapshot",
    "PerformanceCacheSnapshot",
    "PerformanceMetrics",
    "PerformancePreset",
    "PerformanceRunResult",
    "PerformanceRunSpec",
    "PerformanceRunner",
    "PerformanceSweepDefinition",
    "PerformanceSweepKind",
    "PerformanceSweepPointResult",
    "PerformanceSweepResult",
    "PerformanceSweepRunner",
    "PerformanceTimingModel",
    "SEQUENTIAL_BLOCK_BENEFIT",
    "SEQUENTIAL_BLOCK_BENEFIT_SWEEP",
    "STRIDE_BLOCK_COST",
    "STRIDE_BLOCK_COST_SWEEP",
    "TwoLevelPerformanceAnalyzer",
    "TwoLevelPerformanceResult",
    "TwoLevelTimingModel",
]
