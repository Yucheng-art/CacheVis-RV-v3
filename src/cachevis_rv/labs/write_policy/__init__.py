"""Pure-Python write-policy semantics and traffic analysis."""

from .explainer import WritePolicyExplainer, snapshot_cache
from .model import (
    CacheSnapshot,
    MemoryAccess,
    MemoryAccessKind,
    WRITE_POLICY_LANES,
    WriteDecisionKind,
    WritePolicyComparisonStatistics,
    WritePolicyComparisonStep,
    WritePolicyDecisionEvidence,
    WritePolicyLaneSpec,
    WritePolicyLaneStatistics,
    WritePolicyLaneStep,
    WritePolicyLineSnapshot,
    WritePolicyPreset,
    WriteTrafficAssumptions,
    WriteTrafficDelta,
)
from .parser import parse_memory_access_trace
from .presets import WRITE_POLICY_PRESETS, get_write_policy_preset
from .session import WritePolicyComparisonSession
from .traffic import build_traffic_delta
from .cache_view_model import (
    WritePolicyCacheLineViewModel,
    WritePolicyLaneCacheViewModel,
    build_lane_cache_view_model,
)
from .comparison_view_model import (
    CAUTION_NOTE,
    WritePolicyComparisonSummaryViewModel,
    WritePolicyDivergenceSummaryViewModel,
    build_comparison_summary_view_model,
    build_divergence_summary_view_model,
)
from .controller import WritePolicyController
from .decision_view_model import (
    WritePolicyLaneDecisionViewModel,
    build_lane_decision_view_model,
)
from .page_state import (
    EMPTY_WRITE_POLICY_PAGE_STATE,
    WritePolicyPageState,
    empty_write_policy_page_state,
)
from .statistics_view_model import (
    WritePolicyLaneStatisticsViewModel,
    build_lane_statistics_view_model,
)
from .timeline_view_model import (
    WritePolicyTimelineLaneTrafficViewModel,
    WritePolicyTimelineStepViewModel,
    build_timeline_view_models,
)
from .traffic_view_model import WritePolicyTrafficViewModel, build_traffic_view_model

__all__ = [
    "CacheSnapshot",
    "EMPTY_WRITE_POLICY_PAGE_STATE",
    "MemoryAccess",
    "MemoryAccessKind",
    "WRITE_POLICY_LANES",
    "WRITE_POLICY_PRESETS",
    "WriteDecisionKind",
    "WritePolicyCacheLineViewModel",
    "WritePolicyComparisonSummaryViewModel",
    "WritePolicyController",
    "WritePolicyDivergenceSummaryViewModel",
    "WritePolicyLaneCacheViewModel",
    "WritePolicyLaneDecisionViewModel",
    "WritePolicyLaneStatisticsViewModel",
    "WritePolicyPageState",
    "WritePolicyTimelineLaneTrafficViewModel",
    "WritePolicyTimelineStepViewModel",
    "WritePolicyTrafficViewModel",
    "WritePolicyComparisonSession",
    "WritePolicyComparisonStatistics",
    "WritePolicyComparisonStep",
    "WritePolicyDecisionEvidence",
    "WritePolicyExplainer",
    "WritePolicyLaneSpec",
    "WritePolicyLaneStatistics",
    "WritePolicyLaneStep",
    "WritePolicyLineSnapshot",
    "WritePolicyPreset",
    "WriteTrafficAssumptions",
    "WriteTrafficDelta",
    "build_traffic_delta",
    "build_comparison_summary_view_model",
    "build_divergence_summary_view_model",
    "build_lane_cache_view_model",
    "build_lane_decision_view_model",
    "build_lane_statistics_view_model",
    "build_timeline_view_models",
    "build_traffic_view_model",
    "CAUTION_NOTE",
    "empty_write_policy_page_state",
    "get_write_policy_preset",
    "parse_memory_access_trace",
    "snapshot_cache",
]
