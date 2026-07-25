"""Pure timeline presentation models for Miss Type Lab."""

from dataclasses import dataclass

from .model import MissType, MissTypeStep


@dataclass(frozen=True)
class MissTypeTimelineItemViewModel:
    """One horizontally scrollable timeline chip."""

    step_index: int
    step_number: int
    address: int
    address_hex: str
    block_address: int
    result_code: str
    result_label: str
    is_current: bool
    is_selected: bool
    tooltip_lines: tuple[str, ...]


def build_timeline_item(
    step: MissTypeStep,
    *,
    current_step_index: int | None = None,
    selected_step_index: int | None = None,
) -> MissTypeTimelineItemViewModel:
    """Build a chip from an already classified step."""
    result_code, result_label = _result(step)
    return MissTypeTimelineItemViewModel(
        step_index=step.step_index,
        step_number=step.step_index + 1,
        address=step.address,
        address_hex=f"0x{step.address:X}",
        block_address=step.block_address,
        result_code=result_code,
        result_label=result_label,
        is_current=step.step_index == current_step_index,
        is_selected=step.step_index == selected_step_index,
        tooltip_lines=(
            f"Step {step.step_index + 1}",
            f"Address: {step.address} (0x{step.address:X})",
            f"Memory block: {step.block_address}",
            f"Actual Cache: {step.actual_result.upper()}",
            f"Reference Cache: {step.reference_result.upper()}",
            f"Result: {result_label}",
            step.evidence.classification_reason,
        ),
    )


def build_timeline_items(
    steps: tuple[MissTypeStep, ...],
    *,
    current_step_index: int | None = None,
    selected_step_index: int | None = None,
) -> tuple[MissTypeTimelineItemViewModel, ...]:
    """Build all timeline chips with independent CURRENT/SELECTED state."""
    return tuple(
        build_timeline_item(
            step,
            current_step_index=current_step_index,
            selected_step_index=selected_step_index,
        )
        for step in steps
    )


def _result(step: MissTypeStep) -> tuple[str, str]:
    if step.actual_result == "hit":
        return "H", "Hit"
    mapping = {
        MissType.COMPULSORY: ("C", "Compulsory Miss"),
        MissType.CONFLICT: ("F", "Conflict Miss"),
        MissType.CAPACITY: ("A", "Capacity Miss"),
    }
    try:
        return mapping[step.miss_type]
    except KeyError as exc:
        raise ValueError("completed miss step requires a 3C result") from exc


__all__ = [
    "MissTypeTimelineItemViewModel",
    "build_timeline_item",
    "build_timeline_items",
]
