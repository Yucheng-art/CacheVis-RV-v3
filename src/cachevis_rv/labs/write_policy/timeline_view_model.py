"""Immutable timeline models derived from completed formal session steps."""

from dataclasses import dataclass

from .model import WritePolicyComparisonStep


@dataclass(frozen=True)
class WritePolicyTimelineLaneTrafficViewModel:
    lane_id: str
    lane_label: str
    step_total_bytes: int
    cumulative_runtime_bytes: int
    cumulative_with_final_drain_bytes: int


@dataclass(frozen=True)
class WritePolicyTimelineStepViewModel:
    step_index: int
    display_step_number: int
    access_kind: str
    address: int
    address_hex: str
    block_address: int
    set_index: int
    tag: int
    outcome_diverged: bool
    allocation_diverged: bool
    bypass_diverged: bool
    writeback_diverged: bool
    traffic_diverged: bool
    dirty_state_diverged: bool
    cache_state_diverged: bool
    lane_traffic: tuple[WritePolicyTimelineLaneTrafficViewModel, ...]
    is_selected: bool
    is_latest: bool


def build_timeline_view_models(
    steps: tuple[WritePolicyComparisonStep, ...],
    selected_step_index: int | None,
) -> tuple[WritePolicyTimelineStepViewModel, ...]:
    latest_index = steps[-1].step_index if steps else None
    result = []
    for step in steps:
        lane_traffic = tuple(
            WritePolicyTimelineLaneTrafficViewModel(
                lane_id=lane_step.lane.lane_id,
                lane_label=lane_step.lane.label,
                step_total_bytes=lane_step.evidence.traffic_delta.total_lower_memory_bytes,
                cumulative_runtime_bytes=lane_statistics.total_lower_memory_bytes,
                cumulative_with_final_drain_bytes=(
                    lane_statistics.total_lower_memory_bytes_with_final_drain
                ),
            )
            for lane_step, lane_statistics in zip(
                step.lane_steps, step.statistics.lane_statistics
            )
        )
        result.append(
            WritePolicyTimelineStepViewModel(
                step_index=step.step_index,
                display_step_number=step.step_index + 1,
                access_kind=step.access.kind.value,
                address=step.access.address,
                address_hex=step.address_hex,
                block_address=step.block_address,
                set_index=step.set_index,
                tag=step.tag,
                outcome_diverged=step.outcome_diverged,
                allocation_diverged=step.allocation_diverged,
                bypass_diverged=step.bypass_diverged,
                writeback_diverged=step.writeback_diverged,
                traffic_diverged=step.traffic_diverged,
                dirty_state_diverged=step.dirty_state_diverged,
                cache_state_diverged=step.cache_state_diverged,
                lane_traffic=lane_traffic,
                is_selected=step.step_index == selected_step_index,
                is_latest=step.step_index == latest_index,
            )
        )
    return tuple(result)


__all__ = [
    "WritePolicyTimelineLaneTrafficViewModel",
    "WritePolicyTimelineStepViewModel",
    "build_timeline_view_models",
]
