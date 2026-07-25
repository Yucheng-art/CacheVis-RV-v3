"""Structured explanation sections for Address Visualizer steps."""

from dataclasses import dataclass

from ..model import AccessStepViewModel


@dataclass(frozen=True)
class ExplanationSection:
    """One titled explanation group for the GUI panel."""

    title: str
    lines: list[str]
    status: str = "normal"


def build_explanation_sections(step: AccessStepViewModel) -> list[ExplanationSection]:
    """Convert a flat step view model into classroom-style explanation groups."""
    return [
        _build_address_split_section(step),
        _build_lookup_section(step),
        _build_result_section(step),
        _build_replacement_section(step),
    ]


def _build_address_split_section(step: AccessStepViewModel) -> ExplanationSection:
    return ExplanationSection(
        title="Address Split",
        status="normal",
        lines=[
            f"Address {step.address_dec} = {step.address_hex}.",
            (
                f"Offset uses {step.offset_bits} bit(s), because block size decides "
                "the position inside the cache block."
            ),
            (
                f"Index uses {step.index_bits} bit(s), because the number of sets "
                "decides which cache set / row is selected."
            ),
            (
                f"Tag uses {step.tag_bits} bit(s): the remaining high bits after "
                "Index and Offset."
            ),
            (
                f"Tag={step.tag}, Index={step.index}, Offset={step.offset}. "
                "Tag confirms the selected line contains the target memory block."
            ),
        ],
    )


def _build_lookup_section(step: AccessStepViewModel) -> ExplanationSection:
    if step.hit:
        lines = [
            f"Index maps this address to set {step.mapped_set}.",
            (
                f"Way {step.hit_way} has valid=1 and a matching tag "
                f"({step.tag}), so this access is a cache hit."
            ),
        ]
        status = "hit"
    else:
        lines = [
            f"Index maps this address to set {step.mapped_set}.",
            (
                "No line in the selected set has both valid=1 and the target "
                f"tag ({step.tag}), so this access is a cache miss."
            ),
        ]
        status = "miss"
    return ExplanationSection(title="Lookup", lines=lines, status=status)


def _build_result_section(step: AccessStepViewModel) -> ExplanationSection:
    result = "HIT" if step.hit else "MISS"
    lines = [
        f"Result: {result}.",
        (
            f"Totals: {step.total_accesses} access(es), {step.hits} hit(s), "
            f"{step.misses} miss(es)."
        ),
        f"Rates: hit {step.hit_rate:.2%}, miss {step.miss_rate:.2%}.",
    ]

    if step.hit:
        lines.append("Miss type is not applicable to a hit.")
        status = "hit"
    else:
        miss_type = step.miss_type or "unknown"
        if miss_type == "compulsory":
            lines.append(
                "Miss type: compulsory. This memory block is being accessed for "
                "the first time in the trace."
            )
            status = "miss"
        else:
            lines.append(
                f"Miss type: {miss_type}. Conflict/capacity classification is "
                "reserved for a later milestone."
            )
            status = "warning"
    return ExplanationSection(title="Result", lines=lines, status=status)


def _build_replacement_section(step: AccessStepViewModel) -> ExplanationSection:
    if step.hit:
        return ExplanationSection(
            title="Replacement / Fill",
            status="normal",
            lines=["This is a hit, so no cache line is filled or replaced."],
        )

    if step.replacement_reason == "invalid-line" or not step.replaced_valid:
        return ExplanationSection(
            title="Replacement / Fill",
            status="replacement",
            lines=[
                f"Way {step.victim_way} is invalid, so the cache fills it first.",
                "Invalid lines are preferred before evicting any valid cache line.",
            ],
        )

    replaced_tag = "-" if step.replaced_tag is None else f"0x{step.replaced_tag:x}"
    policy = step.replacement_reason or "the selected replacement policy"
    return ExplanationSection(
        title="Replacement / Fill",
        status="replacement",
        lines=[
            f"All candidate lines were valid, so {policy} selected way {step.victim_way}.",
            f"The replaced line had tag {replaced_tag}.",
        ],
    )
