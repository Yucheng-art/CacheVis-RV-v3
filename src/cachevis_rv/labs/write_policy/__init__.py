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

__all__ = [
    "CacheSnapshot",
    "MemoryAccess",
    "MemoryAccessKind",
    "WRITE_POLICY_LANES",
    "WRITE_POLICY_PRESETS",
    "WriteDecisionKind",
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
    "get_write_policy_preset",
    "parse_memory_access_trace",
    "snapshot_cache",
]
