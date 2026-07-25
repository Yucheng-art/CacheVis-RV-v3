"""Pure display model helpers for the Address Visualizer timeline."""

from dataclasses import dataclass

from visualizer_model import AccessStepViewModel


@dataclass(frozen=True)
class TimelineItemViewModel:
    """One rendered access item in the timeline."""

    step_index: int
    address_dec: str
    address_hex: str
    result: str
    miss_type: str
    is_current: bool
    is_selected: bool
    mapped_set: int
    hit_way: int | None
    victim_way: int | None
    label: str
    tooltip_lines: list[str]


def build_timeline_item(
    step: AccessStepViewModel, *, is_current: bool = True, is_selected: bool = False
) -> TimelineItemViewModel:
    """Build a compact, GUI-friendly timeline item from one access step."""
    result = "HIT" if step.hit else "MISS"
    miss_type = step.miss_type if step.miss_type else "-"
    markers = []
    if is_current:
        markers.append("CURRENT")
    if is_selected:
        markers.append("SELECTED")
    prefix = f"{' | '.join(markers)} | " if markers else ""
    label = (
        f"{prefix}Step {step.step_index}\n"
        f"Addr {step.address_dec} / {step.address_hex}\n"
        f"{result} | {miss_type}"
    )
    tooltip_lines = [
        f"step index: {step.step_index}",
        f"address decimal: {step.address_dec}",
        f"address hex: {step.address_hex}",
        f"mapped set: {step.mapped_set}",
        f"result: {result}",
        f"miss type: {miss_type}",
        f"hit way: {_format_optional(step.hit_way)}",
        f"victim way: {_format_optional(step.victim_way)}",
    ]
    return TimelineItemViewModel(
        step_index=step.step_index,
        address_dec=step.address_dec,
        address_hex=step.address_hex,
        result=result,
        miss_type=miss_type,
        is_current=is_current,
        is_selected=is_selected,
        mapped_set=step.mapped_set,
        hit_way=step.hit_way,
        victim_way=step.victim_way,
        label=label,
        tooltip_lines=tooltip_lines,
    )


def _format_optional(value: int | None) -> str:
    if value is None:
        return "-"
    return str(value)
