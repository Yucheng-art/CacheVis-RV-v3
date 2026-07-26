"""Pure-logic public API for performance modeling and sweeps."""

from .chart_view_model import (
    PerformanceChartMetric,
    PerformanceChartPointViewModel,
    PerformanceChartSeriesViewModel,
    build_chart_series_view_model,
)
from .comparison_view_model import (
    PerformanceComparisonViewModel,
    PerformanceTradeoffPairViewModel,
    build_comparison_view_model,
)
from .controller import PerformanceController
from .hierarchy import (
    TwoLevelPerformanceAnalyzer,
    TwoLevelPerformanceResult,
    TwoLevelTimingModel,
)
from .hierarchy_view_model import (
    HierarchyContributionRowViewModel,
    HierarchyProbabilityRowViewModel,
    TwoLevelPerformanceViewModel,
    build_hierarchy_view_model,
)
from .metrics_view_model import (
    PerformanceMetricsViewModel,
    build_metrics_view_model,
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
from .page_state import EMPTY_PERFORMANCE_PAGE_STATE, PerformancePageState
from .runner import PerformanceRunner
from .sweep import (
    PerformanceSweepDefinition,
    PerformanceSweepKind,
    PerformanceSweepPointResult,
    PerformanceSweepResult,
    PerformanceSweepRunner,
)
from .sweep_view_model import (
    PerformanceSweepPointViewModel,
    PerformanceSweepSummaryViewModel,
    build_sweep_point_view_models,
    build_sweep_summary_view_model,
)
from .timing import PerformanceTimingModel

__all__ = [
    "ANALYTICAL_L1_L2_EXAMPLE",
    "ANALYTICAL_L1_L2_MODEL",
    "ASSOCIATIVITY_CONFLICT_RELIEF",
    "ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP",
    "CAPACITY_KNEE",
    "CAPACITY_KNEE_SWEEP",
    "EMPTY_PERFORMANCE_PAGE_STATE",
    "HIT_RATE_IS_NOT_AMAT",
    "HIT_RATE_IS_NOT_AMAT_SWEEP",
    "HierarchyContributionRowViewModel",
    "HierarchyProbabilityRowViewModel",
    "MISS_PENALTY_SENSITIVITY",
    "MISS_PENALTY_SENSITIVITY_SWEEP",
    "PERFORMANCE_PRESETS",
    "PERFORMANCE_SWEEP_PRESETS",
    "PerformanceCacheLineSnapshot",
    "PerformanceCacheSnapshot",
    "PerformanceChartMetric",
    "PerformanceChartPointViewModel",
    "PerformanceChartSeriesViewModel",
    "PerformanceComparisonViewModel",
    "PerformanceController",
    "PerformanceMetrics",
    "PerformanceMetricsViewModel",
    "PerformancePageState",
    "PerformancePreset",
    "PerformanceRunResult",
    "PerformanceRunSpec",
    "PerformanceRunner",
    "PerformanceSweepDefinition",
    "PerformanceSweepKind",
    "PerformanceSweepPointResult",
    "PerformanceSweepPointViewModel",
    "PerformanceSweepResult",
    "PerformanceSweepRunner",
    "PerformanceSweepSummaryViewModel",
    "PerformanceTimingModel",
    "PerformanceTradeoffPairViewModel",
    "SEQUENTIAL_BLOCK_BENEFIT",
    "SEQUENTIAL_BLOCK_BENEFIT_SWEEP",
    "STRIDE_BLOCK_COST",
    "STRIDE_BLOCK_COST_SWEEP",
    "TwoLevelPerformanceAnalyzer",
    "TwoLevelPerformanceResult",
    "TwoLevelPerformanceViewModel",
    "TwoLevelTimingModel",
    "build_chart_series_view_model",
    "build_comparison_view_model",
    "build_hierarchy_view_model",
    "build_metrics_view_model",
    "build_sweep_point_view_models",
    "build_sweep_summary_view_model",
]
