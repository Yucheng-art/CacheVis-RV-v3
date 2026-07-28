"""Cross-lane divergence and comparison summaries."""

from dataclasses import dataclass

from .model import (
    WRITE_POLICY_LANES,
    WritePolicyComparisonStatistics,
    WritePolicyComparisonStep,
)


CAUTION_NOTE = (
    "Results apply only to the current trace, cache configuration, and traffic assumptions."
)


@dataclass(frozen=True)
class WritePolicyDivergenceSummaryViewModel:
    accesses: int
    all_outcomes_agree_steps: int
    outcome_divergence_steps: int
    allocation_divergence_steps: int
    bypass_divergence_steps: int
    writeback_divergence_steps: int
    traffic_divergence_steps: int
    dirty_state_divergence_steps: int
    cache_state_divergence_steps: int
    first_outcome_divergence_step: int | None
    first_allocation_divergence_step: int | None
    first_bypass_divergence_step: int | None
    first_writeback_divergence_step: int | None
    first_traffic_divergence_step: int | None
    first_dirty_state_divergence_step: int | None
    first_cache_state_divergence_step: int | None
    outcome_partition_ok: bool


@dataclass(frozen=True)
class WritePolicyComparisonSummaryViewModel:
    runtime_lowest_traffic_lane_ids: tuple[str, ...]
    runtime_lowest_traffic_lane_labels: tuple[str, ...]
    runtime_lowest_traffic_is_tie: bool
    with_drain_lowest_traffic_lane_ids: tuple[str, ...]
    with_drain_lowest_traffic_lane_labels: tuple[str, ...]
    with_drain_lowest_traffic_is_tie: bool
    highest_hit_rate_lane_ids: tuple[str, ...]
    highest_hit_rate_lane_labels: tuple[str, ...]
    highest_hit_rate_is_tie: bool
    runtime_and_drain_leaders_agree: bool
    allocation_changed_future_outcome: bool
    propagation_changed_dirty_state: bool
    propagation_changed_runtime_traffic: bool
    dirty_eviction_observed: bool
    bypass_observed: bool
    actual_observations: tuple[str, ...]
    caution_note: str


def _first(steps, attribute):
    return next((step.step_index for step in steps if getattr(step, attribute)), None)


def build_divergence_summary_view_model(
    statistics: WritePolicyComparisonStatistics,
    steps: tuple[WritePolicyComparisonStep, ...],
) -> WritePolicyDivergenceSummaryViewModel:
    return WritePolicyDivergenceSummaryViewModel(
        accesses=statistics.accesses,
        all_outcomes_agree_steps=statistics.all_outcomes_agree_steps,
        outcome_divergence_steps=statistics.outcome_divergence_steps,
        allocation_divergence_steps=statistics.allocation_divergence_steps,
        bypass_divergence_steps=statistics.bypass_divergence_steps,
        writeback_divergence_steps=statistics.writeback_divergence_steps,
        traffic_divergence_steps=statistics.traffic_divergence_steps,
        dirty_state_divergence_steps=statistics.dirty_state_divergence_steps,
        cache_state_divergence_steps=statistics.cache_state_divergence_steps,
        first_outcome_divergence_step=_first(steps, "outcome_diverged"),
        first_allocation_divergence_step=_first(steps, "allocation_diverged"),
        first_bypass_divergence_step=_first(steps, "bypass_diverged"),
        first_writeback_divergence_step=_first(steps, "writeback_diverged"),
        first_traffic_divergence_step=_first(steps, "traffic_diverged"),
        first_dirty_state_divergence_step=_first(steps, "dirty_state_diverged"),
        first_cache_state_divergence_step=_first(steps, "cache_state_diverged"),
        outcome_partition_ok=(
            statistics.accesses
            == statistics.all_outcomes_agree_steps + statistics.outcome_divergence_steps
        ),
    )


def _leaders(lane_statistics, attribute, rate=False):
    values = tuple(
        ((item.hits / item.accesses) if rate and item.accesses else 0.0)
        if rate
        else getattr(item, attribute)
        for item in lane_statistics
    )
    target = max(values) if rate else min(values)
    winners = tuple(item.lane for item, value in zip(lane_statistics, values) if value == target)
    return tuple(lane.lane_id for lane in winners), tuple(lane.label for lane in winners)


def build_comparison_summary_view_model(
    statistics: WritePolicyComparisonStatistics,
    steps: tuple[WritePolicyComparisonStep, ...],
) -> WritePolicyComparisonSummaryViewModel:
    lane_statistics = statistics.lane_statistics
    # Formal sessions always expose all four lanes, including for an empty trace.
    if not lane_statistics:
        lane_statistics = ()
        runtime_ids = drain_ids = hit_ids = tuple(lane.lane_id for lane in WRITE_POLICY_LANES)
        runtime_labels = drain_labels = hit_labels = tuple(lane.label for lane in WRITE_POLICY_LANES)
    else:
        runtime_ids, runtime_labels = _leaders(lane_statistics, "total_lower_memory_bytes")
        drain_ids, drain_labels = _leaders(
            lane_statistics, "total_lower_memory_bytes_with_final_drain"
        )
        hit_ids, hit_labels = _leaders(lane_statistics, "hits", rate=True)

    outcome_indices = tuple(step.step_index for step in steps if step.outcome_diverged)
    allocation_indices = tuple(step.step_index for step in steps if step.allocation_diverged)
    allocation_changed_future_outcome = any(
        allocation_index < outcome_index
        for allocation_index in allocation_indices
        for outcome_index in outcome_indices
    )
    dirty_eviction = any(item.dirty_writebacks for item in lane_statistics)
    bypass = any(item.bypass_writes for item in lane_statistics)
    propagation_changed_dirty_state = any(
        lane_steps[first].after_cache_snapshot != lane_steps[second].after_cache_snapshot
        and tuple(line.valid and line.dirty for line in lane_steps[first].after_cache_snapshot)
        != tuple(line.valid and line.dirty for line in lane_steps[second].after_cache_snapshot)
        for step in steps
        for lane_steps in (step.lane_steps,)
        for first, second in ((0, 2), (1, 3))
    )
    propagation_changed_runtime_traffic = bool(lane_statistics) and any(
        lane_statistics[first].total_lower_memory_bytes
        != lane_statistics[second].total_lower_memory_bytes
        for first, second in ((0, 2), (1, 3))
    )
    observations = []
    if statistics.outcome_divergence_steps == 0:
        observations.append("All four lanes produced identical hit/miss outcomes.")
    else:
        observations.append(
            f"Hit/miss outcomes diverged on {statistics.outcome_divergence_steps} step(s)."
        )
    if statistics.allocation_divergence_steps:
        observations.append("Write allocation behavior differed between lanes.")
    if bypass:
        observations.append("At least one no-write-allocate lane bypassed the cache.")
    if dirty_eviction:
        observations.append("At least one dirty eviction produced a whole-block write-back.")
    if statistics.traffic_divergence_steps:
        observations.append("Runtime lower-memory traffic differed between lanes.")
    elif lane_statistics:
        observations.append("All four lanes produced identical runtime traffic.")
    if lane_statistics and all(
        lane_statistics[first].hits == lane_statistics[second].hits
        and lane_statistics[first].misses == lane_statistics[second].misses
        for first, second in ((0, 1), (2, 3))
    ):
        observations.append(
            "WA and NWA had the same aggregate hit/miss outcome within each propagation policy."
        )

    return WritePolicyComparisonSummaryViewModel(
        runtime_lowest_traffic_lane_ids=runtime_ids,
        runtime_lowest_traffic_lane_labels=runtime_labels,
        runtime_lowest_traffic_is_tie=len(runtime_ids) != 1,
        with_drain_lowest_traffic_lane_ids=drain_ids,
        with_drain_lowest_traffic_lane_labels=drain_labels,
        with_drain_lowest_traffic_is_tie=len(drain_ids) != 1,
        highest_hit_rate_lane_ids=hit_ids,
        highest_hit_rate_lane_labels=hit_labels,
        highest_hit_rate_is_tie=len(hit_ids) != 1,
        runtime_and_drain_leaders_agree=runtime_ids == drain_ids,
        allocation_changed_future_outcome=allocation_changed_future_outcome,
        propagation_changed_dirty_state=propagation_changed_dirty_state,
        propagation_changed_runtime_traffic=propagation_changed_runtime_traffic,
        dirty_eviction_observed=dirty_eviction,
        bypass_observed=bypass,
        actual_observations=tuple(observations),
        caution_note=CAUTION_NOTE,
    )


__all__ = [
    "CAUTION_NOTE",
    "WritePolicyComparisonSummaryViewModel",
    "WritePolicyDivergenceSummaryViewModel",
    "build_comparison_summary_view_model",
    "build_divergence_summary_view_model",
]
