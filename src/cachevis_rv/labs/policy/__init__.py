"""Public pure-Python API for replacement-policy comparison."""

from .cache_view_model import (
    PolicyCacheLineViewModel,
    PolicyLaneCacheViewModel,
    build_lane_cache_view_models,
)
from .controller import PolicyController
from .decision_view_model import (
    PolicyComparisonEvidenceViewModel,
    PolicyLaneDecisionViewModel,
    build_comparison_evidence_view_model,
    build_lane_decision_view_model,
)
from .divergence_view_model import (
    PolicyDivergenceSummaryViewModel,
    build_divergence_summary,
)
from .explainer import POLICIES, PolicyDecisionExplainer
from .model import (
    PolicyComparisonStatistics,
    PolicyComparisonStep,
    PolicyDecisionEvidence,
    PolicyDecisionKind,
    PolicyLaneStatistics,
    PolicyLaneStep,
    PolicyLineSnapshot,
)
from .presets import (
    DIRECT_MAPPED_CONTROL,
    FIFO_ADVANTAGE,
    LRU_ADVANTAGE,
    NO_REPLACEMENT_PRESSURE,
    POLICY_PRESETS,
    SEEDED_RANDOM_REPLAY,
    SET_LOCAL_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    PolicyPreset,
)
from .random_stream import IsolatedRandomStream
from .session import CacheSnapshot, PolicyComparisonSession
from .page_state import EMPTY_PAGE_STATE, PolicyPageState
from .statistics_view_model import (
    PolicyComparisonStatisticsViewModel,
    PolicyLaneStatisticsViewModel,
    build_statistics_view_model,
)
from .timeline_view_model import (
    PolicyTimelineItemViewModel,
    PolicyTimelineLaneBadgeViewModel,
    build_timeline_item,
    build_timeline_items,
)

__all__ = [
    "POLICIES",
    "PolicyDecisionExplainer",
    "PolicyDecisionKind",
    "PolicyLineSnapshot",
    "PolicyDecisionEvidence",
    "PolicyLaneStep",
    "PolicyComparisonStep",
    "PolicyLaneStatistics",
    "PolicyComparisonStatistics",
    "PolicyComparisonSession",
    "CacheSnapshot",
    "IsolatedRandomStream",
    "PolicyController",
    "PolicyPageState",
    "EMPTY_PAGE_STATE",
    "PolicyCacheLineViewModel",
    "PolicyLaneCacheViewModel",
    "build_lane_cache_view_models",
    "PolicyLaneDecisionViewModel",
    "PolicyComparisonEvidenceViewModel",
    "build_lane_decision_view_model",
    "build_comparison_evidence_view_model",
    "PolicyLaneStatisticsViewModel",
    "PolicyComparisonStatisticsViewModel",
    "build_statistics_view_model",
    "PolicyDivergenceSummaryViewModel",
    "build_divergence_summary",
    "PolicyTimelineLaneBadgeViewModel",
    "PolicyTimelineItemViewModel",
    "build_timeline_item",
    "build_timeline_items",
    "PolicyPreset",
    "NO_REPLACEMENT_PRESSURE",
    "VICTIM_DIVERGENCE_BEFORE_OUTCOME",
    "LRU_ADVANTAGE",
    "FIFO_ADVANTAGE",
    "SET_LOCAL_PRESSURE",
    "DIRECT_MAPPED_CONTROL",
    "SEEDED_RANDOM_REPLAY",
    "POLICY_PRESETS",
]
