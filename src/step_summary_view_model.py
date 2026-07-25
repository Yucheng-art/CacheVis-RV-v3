"""Pure display model for selected timeline step summaries."""

from dataclasses import dataclass

from visualizer_model import AccessStepViewModel


SUMMARY_ONLY_NOTE = (
    "This is a step summary only. Cache view remains at the current/latest state."
)


@dataclass(frozen=True)
class StepSummaryViewModel:
    """Summary data shown when a timeline chip is selected."""

    step_index: int
    address_dec: str
    address_hex: str
    address_binary: str
    result: str
    miss_type: str
    mapped_set: int
    hit_way: str
    victim_way: str
    replaced_tag: str
    replacement_reason: str
    hit_rate: str
    miss_rate: str
    summary_lines: list[str]
    note: str


def build_step_summary(step: AccessStepViewModel) -> StepSummaryViewModel:
    """Build a copy-friendly summary for a selected access step."""
    result = "HIT" if step.hit else "MISS"
    miss_type = step.miss_type if step.miss_type else "-"
    hit_way = _format_optional(step.hit_way)
    victim_way = _format_optional(step.victim_way)
    replaced_tag = _format_tag(step.replaced_tag)
    replacement_reason = step.replacement_reason if step.replacement_reason else "-"
    hit_rate = _format_rate(step.hit_rate)
    miss_rate = _format_rate(step.miss_rate)

    lines = [
        f"Step {step.step_index} selected.",
        f"Address: {step.address_dec} / {step.address_hex}",
        f"Result: {result}",
        f"Mapped set: {step.mapped_set}",
    ]
    if step.hit:
        lines.extend(
            [
                f"Hit way: {hit_way}",
                "Reason: valid bit is 1 and tag matches.",
            ]
        )
    else:
        lines.extend(
            [
                f"Miss type: {miss_type}",
                f"Victim way: {victim_way}",
                f"Replaced tag: {replaced_tag}",
            ]
        )
        if step.replacement_reason == "invalid-line" or not step.replaced_valid:
            lines.append("Fill: invalid line is filled first.")
        else:
            lines.append(f"Replacement: {replacement_reason} selected the victim way.")
        if miss_type not in ("-", "compulsory"):
            lines.append("Note: conflict/capacity classification is reserved.")

    lines.extend(
        [
            f"Cumulative: {step.hits} hit(s), {step.misses} miss(es).",
            f"Rates: hit {hit_rate}, miss {miss_rate}.",
            f"Note: {SUMMARY_ONLY_NOTE}",
        ]
    )

    return StepSummaryViewModel(
        step_index=step.step_index,
        address_dec=step.address_dec,
        address_hex=step.address_hex,
        address_binary=step.address_binary,
        result=result,
        miss_type=miss_type,
        mapped_set=step.mapped_set,
        hit_way=hit_way,
        victim_way=victim_way,
        replaced_tag=replaced_tag,
        replacement_reason=replacement_reason,
        hit_rate=hit_rate,
        miss_rate=miss_rate,
        summary_lines=lines,
        note=SUMMARY_ONLY_NOTE,
    )


def _format_optional(value: int | None) -> str:
    if value is None:
        return "-"
    return str(value)


def _format_tag(tag: int | None) -> str:
    if tag is None:
        return "-"
    return f"0x{tag:x}"


def _format_rate(rate: float) -> str:
    return f"{rate:.2%}"
