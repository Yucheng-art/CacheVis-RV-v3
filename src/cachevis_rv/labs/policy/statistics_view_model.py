"""Stable view models for policy comparison statistics."""

from dataclasses import dataclass

from .model import PolicyComparisonStatistics


@dataclass(frozen=True)
class PolicyLaneStatisticsViewModel:
    policy: str
    accesses: int
    hits: int
    misses: int
    invalid_fills: int
    evictions: int
    hit_rate: float
    miss_rate: float
    access_invariant_ok: bool
    miss_partition_invariant_ok: bool


@dataclass(frozen=True)
class PolicyComparisonStatisticsViewModel:
    accesses: int
    lane_statistics: tuple[PolicyLaneStatisticsViewModel, ...]
    all_agree_steps: int
    outcome_divergence_steps: int
    victim_divergence_steps: int
    state_divergence_steps: int
    outcome_partition_invariant_ok: bool


def build_statistics_view_model(
    statistics: PolicyComparisonStatistics,
) -> PolicyComparisonStatisticsViewModel:
    lanes = tuple(
        PolicyLaneStatisticsViewModel(
            policy=lane.policy,
            accesses=lane.accesses,
            hits=lane.hits,
            misses=lane.misses,
            invalid_fills=lane.invalid_fills,
            evictions=lane.evictions,
            hit_rate=lane.hit_rate,
            miss_rate=lane.miss_rate,
            access_invariant_ok=lane.hits + lane.misses == lane.accesses,
            miss_partition_invariant_ok=(
                lane.invalid_fills + lane.evictions == lane.misses
            ),
        )
        for lane in statistics.lane_statistics
    )
    return PolicyComparisonStatisticsViewModel(
        accesses=statistics.accesses,
        lane_statistics=lanes,
        all_agree_steps=statistics.all_agree_steps,
        outcome_divergence_steps=statistics.outcome_divergence_steps,
        victim_divergence_steps=statistics.victim_divergence_steps,
        state_divergence_steps=statistics.state_divergence_steps,
        outcome_partition_invariant_ok=(
            statistics.all_agree_steps
            + statistics.outcome_divergence_steps
            == statistics.accesses
        ),
    )


__all__ = [
    "PolicyLaneStatisticsViewModel",
    "PolicyComparisonStatisticsViewModel",
    "build_statistics_view_model",
]
