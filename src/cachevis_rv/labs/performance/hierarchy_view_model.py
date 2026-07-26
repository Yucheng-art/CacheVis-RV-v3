"""Explanatory rows for the analytical two-level AMAT result."""

from dataclasses import dataclass

from .hierarchy import TwoLevelPerformanceResult


@dataclass(frozen=True)
class HierarchyProbabilityRowViewModel:
    row_id: str
    label: str
    probability: float
    formula: str
    explanation: str


@dataclass(frozen=True)
class HierarchyContributionRowViewModel:
    row_id: str
    label: str
    cycles: float
    formula: str
    explanation: str


@dataclass(frozen=True)
class TwoLevelPerformanceViewModel:
    l1_hit_time_cycles: float
    l1_miss_rate: float
    l2_hit_time_cycles: float
    l2_local_miss_rate: float
    l2_global_miss_rate: float
    memory_penalty_cycles: float
    probability_rows: tuple[HierarchyProbabilityRowViewModel, ...]
    contribution_rows: tuple[HierarchyContributionRowViewModel, ...]
    amat_cycles: float
    probability_partition_ok: bool
    contribution_sum_ok: bool
    rule_path: tuple[str, ...]
    local_vs_global_explanation: str
    limitation_notes: tuple[str, ...]
    teaching_insight: str


def build_hierarchy_view_model(
    result: TwoLevelPerformanceResult,
) -> TwoLevelPerformanceViewModel:
    if not isinstance(result, TwoLevelPerformanceResult):
        raise TypeError("result must be TwoLevelPerformanceResult")
    model = result.model
    return TwoLevelPerformanceViewModel(
        l1_hit_time_cycles=model.l1_hit_time_cycles,
        l1_miss_rate=model.l1_miss_rate,
        l2_hit_time_cycles=model.l2_hit_time_cycles,
        l2_local_miss_rate=model.l2_local_miss_rate,
        l2_global_miss_rate=result.l2_global_miss_rate,
        memory_penalty_cycles=model.memory_penalty_cycles,
        probability_rows=(
            HierarchyProbabilityRowViewModel(
                "l1_hit",
                "L1 hit",
                result.l1_hit_probability,
                "1 - L1 miss rate",
                "The access is completed by L1.",
            ),
            HierarchyProbabilityRowViewModel(
                "l2_global_hit",
                "L2 global hit",
                result.l2_hit_probability_global,
                "L1 miss rate × (1 - L2 local miss rate)",
                "The access misses L1 and is completed by L2.",
            ),
            HierarchyProbabilityRowViewModel(
                "memory_access",
                "Main memory access",
                result.memory_access_probability,
                "L1 miss rate × L2 local miss rate",
                "The access misses both levels and reaches memory.",
            ),
        ),
        contribution_rows=(
            HierarchyContributionRowViewModel(
                "l1_lookup",
                "L1 lookup contribution",
                result.l1_contribution_cycles,
                "L1 hit time",
                "Every CPU memory access pays the L1 lookup time.",
            ),
            HierarchyContributionRowViewModel(
                "l2_lookup",
                "L2 lookup contribution",
                result.l2_contribution_cycles,
                "L1 miss rate × L2 hit time",
                "Only L1 misses perform the L2 lookup.",
            ),
            HierarchyContributionRowViewModel(
                "memory",
                "Memory contribution",
                result.memory_contribution_cycles,
                "L1 miss rate × L2 local miss rate × memory penalty",
                "Only L2 local misses pay the extra memory penalty.",
            ),
        ),
        amat_cycles=result.amat_cycles,
        probability_partition_ok=result.probability_partition_ok,
        contribution_sum_ok=result.contribution_sum_ok,
        rule_path=(
            "Every access pays L1 hit time",
            "Only L1 misses reach L2",
            "Only L2 local misses reach memory",
            "Sum the three expected-cycle contributions",
            "AMAT",
        ),
        local_vs_global_explanation=(
            "L2 local miss rate uses only accesses that reached L2 as its denominator. "
            "L2 global miss rate is the fraction of all CPU memory accesses that reach "
            "main memory: global = L1 miss rate × L2 local miss rate."
        ),
        limitation_notes=(
            "Analytical model only",
            "No actual L2 contents",
            "No inclusion/exclusion behavior",
            "No write-back traffic",
            "No parallel lookup model",
        ),
        teaching_insight=(
            "A local L2 miss rate is conditional; multiply it by the L1 miss rate "
            "before interpreting global memory traffic."
        ),
    )


__all__ = [
    "HierarchyContributionRowViewModel",
    "HierarchyProbabilityRowViewModel",
    "TwoLevelPerformanceViewModel",
    "build_hierarchy_view_model",
]
