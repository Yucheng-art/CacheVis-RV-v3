"""Public pure-Python API for replacement-policy comparison."""

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
