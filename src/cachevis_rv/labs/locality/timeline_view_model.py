"""Pure timeline models for independent locality and cache results."""

from dataclasses import dataclass

from .model import LocalityKind, LocalityStep


@dataclass(frozen=True)
class LocalityTimelineItemViewModel:
    step_index: int
    address: int
    address_hex: str
    block_address: int
    offset: int
    cache_hit: bool
    locality_kind: LocalityKind
    short_label: str
    is_current: bool
    is_selected: bool
    address_reuse_gap: int | None
    block_reuse_gap: int | None
    block_reuse_distance: int | None
    tooltip: str


def build_timeline_item(
    step: LocalityStep,
    *,
    current_step_index: int | None = None,
    selected_step_index: int | None = None,
) -> LocalityTimelineItemViewModel:
    labels = {
        LocalityKind.FIRST_TOUCH: "F",
        LocalityKind.SPATIAL: "S",
        LocalityKind.TEMPORAL: "T",
    }
    evidence = step.evidence
    return LocalityTimelineItemViewModel(
        step_index=step.step_index,
        address=step.address,
        address_hex=step.address_hex,
        block_address=step.block_address,
        offset=step.offset,
        cache_hit=step.cache_hit,
        locality_kind=step.locality_kind,
        short_label=labels[step.locality_kind],
        is_current=step.step_index == current_step_index,
        is_selected=step.step_index == selected_step_index,
        address_reuse_gap=evidence.address_reuse_gap,
        block_reuse_gap=evidence.block_reuse_gap,
        block_reuse_distance=evidence.block_reuse_distance,
        tooltip=(
            f"Step {step.step_index + 1}; address {step.address_hex}; "
            f"block {step.block_address}; offset {step.offset}; "
            f"cache {'HIT' if step.cache_hit else 'MISS'}; "
            f"locality {step.locality_kind.value}"
        ),
    )


def build_timeline_items(
    steps: tuple[LocalityStep, ...],
    *,
    current_step_index: int | None = None,
    selected_step_index: int | None = None,
) -> tuple[LocalityTimelineItemViewModel, ...]:
    return tuple(
        build_timeline_item(
            step,
            current_step_index=current_step_index,
            selected_step_index=selected_step_index,
        )
        for step in steps
    )


__all__ = [
    "LocalityTimelineItemViewModel",
    "build_timeline_item",
    "build_timeline_items",
]
