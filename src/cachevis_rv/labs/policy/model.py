"""Immutable models for replacement-policy comparison."""

from dataclasses import dataclass
from enum import Enum


class PolicyDecisionKind(str, Enum):
    HIT = "hit"
    INVALID_FILL = "invalid_fill"
    EVICTION = "eviction"


@dataclass(frozen=True)
class PolicyLineSnapshot:
    set_index: int
    way: int
    valid: bool
    tag: int | None
    dirty: bool
    last_used: int
    insert_time: int


@dataclass(frozen=True)
class PolicyDecisionEvidence:
    """Observed decision evidence.

    ``lru_order_before`` is ordered LRU→MRU (oldest use first).
    ``fifo_order_before`` is ordered oldest→newest insertion.
    """

    policy: str
    decision_kind: PolicyDecisionKind
    set_index: int
    tag: int
    hit_way: int | None
    fill_way: int | None
    victim_way: int | None
    victim_tag: int | None
    valid_ways_before: tuple[int, ...]
    invalid_ways_before: tuple[int, ...]
    eligible_victim_ways: tuple[int, ...]
    lru_order_before: tuple[int, ...]
    fifo_order_before: tuple[int, ...]
    random_candidate_ways: tuple[int, ...]
    selected_metric: int | None
    classification_reason: str
    metadata_consistent: bool
    random_seed: int | None = None
    random_draw_index: int | None = None


@dataclass(frozen=True)
class PolicyLaneStep:
    """One policy lane's result and detached target-set snapshots."""

    policy: str
    cache_result: str
    cache_hit: bool
    decision: PolicyDecisionEvidence
    before_set_lines: tuple[PolicyLineSnapshot, ...]
    after_set_lines: tuple[PolicyLineSnapshot, ...]


@dataclass(frozen=True)
class PolicyLaneStatistics:
    policy: str
    accesses: int = 0
    hits: int = 0
    misses: int = 0
    invalid_fills: int = 0
    evictions: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0

    def __post_init__(self) -> None:
        counts = (
            self.accesses, self.hits, self.misses,
            self.invalid_fills, self.evictions,
        )
        if any(not isinstance(value, int) or value < 0 for value in counts):
            raise ValueError("lane statistics counts must be non-negative integers")
        if self.hits + self.misses != self.accesses:
            raise ValueError("hits + misses must equal accesses")
        if self.invalid_fills + self.evictions != self.misses:
            raise ValueError("invalid fills + evictions must equal misses")
        if not 0.0 <= self.hit_rate <= 1.0:
            raise ValueError("hit_rate must be between 0 and 1")
        if not 0.0 <= self.miss_rate <= 1.0:
            raise ValueError("miss_rate must be between 0 and 1")


@dataclass(frozen=True)
class PolicyComparisonStatistics:
    accesses: int = 0
    lane_statistics: tuple[PolicyLaneStatistics, ...] = ()
    all_agree_steps: int = 0
    outcome_divergence_steps: int = 0
    victim_divergence_steps: int = 0
    state_divergence_steps: int = 0

    def __post_init__(self) -> None:
        counts = (
            self.accesses, self.all_agree_steps,
            self.outcome_divergence_steps, self.victim_divergence_steps,
            self.state_divergence_steps,
        )
        if any(not isinstance(value, int) or value < 0 for value in counts):
            raise ValueError("comparison counts must be non-negative integers")
        if self.all_agree_steps + self.outcome_divergence_steps != self.accesses:
            raise ValueError("agree + outcome divergence must equal accesses")
        if any(lane.accesses != self.accesses for lane in self.lane_statistics):
            raise ValueError("every lane must have the comparison access count")


@dataclass(frozen=True)
class PolicyComparisonStep:
    """One synchronized address access across all policy lanes."""

    step_index: int
    address: int
    address_hex: str
    block_address: int
    set_index: int
    tag: int
    lane_steps: tuple[PolicyLaneStep, ...]
    outcome_diverged: bool
    victim_diverged: bool
    state_diverged: bool
    statistics: PolicyComparisonStatistics


__all__ = [
    "PolicyDecisionKind",
    "PolicyLineSnapshot",
    "PolicyDecisionEvidence",
    "PolicyLaneStep",
    "PolicyLaneStatistics",
    "PolicyComparisonStatistics",
    "PolicyComparisonStep",
]
