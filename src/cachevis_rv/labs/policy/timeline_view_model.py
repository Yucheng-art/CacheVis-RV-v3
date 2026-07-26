"""Timeline models for synchronized policy comparison steps."""

from dataclasses import dataclass

from .model import PolicyComparisonStep, PolicyDecisionKind


_DECISION_CODES = {
    PolicyDecisionKind.HIT: "H",
    PolicyDecisionKind.INVALID_FILL: "I",
    PolicyDecisionKind.EVICTION: "E",
}


@dataclass(frozen=True)
class PolicyTimelineLaneBadgeViewModel:
    policy: str
    cache_status: str
    decision_kind: PolicyDecisionKind
    decision_code: str
    hit_way: int | None
    fill_way: int | None
    victim_way: int | None


@dataclass(frozen=True)
class PolicyTimelineItemViewModel:
    step_index: int
    address: int
    address_hex: str
    block_address: int
    set_index: int
    tag: int
    lane_badges: tuple[PolicyTimelineLaneBadgeViewModel, ...]
    outcome_diverged: bool
    victim_diverged: bool
    state_diverged: bool
    is_current: bool
    is_selected: bool
    short_summary: str
    tooltip: str


def build_timeline_items(
    steps: tuple[PolicyComparisonStep, ...],
    *,
    current_step_index: int | None,
    selected_step_index: int | None,
) -> tuple[PolicyTimelineItemViewModel, ...]:
    return tuple(
        build_timeline_item(
            step,
            current_step_index=current_step_index,
            selected_step_index=selected_step_index,
        )
        for step in steps
    )


def build_timeline_item(
    step: PolicyComparisonStep,
    *,
    current_step_index: int | None,
    selected_step_index: int | None,
) -> PolicyTimelineItemViewModel:
    badges = tuple(
        PolicyTimelineLaneBadgeViewModel(
            policy=lane.policy,
            cache_status="HIT" if lane.cache_hit else "MISS",
            decision_kind=lane.decision.decision_kind,
            decision_code=_DECISION_CODES[lane.decision.decision_kind],
            hit_way=lane.decision.hit_way,
            fill_way=lane.decision.fill_way,
            victim_way=lane.decision.victim_way,
        )
        for lane in step.lane_steps
    )
    divergence_codes = "".join(
        code
        for active, code in (
            (step.outcome_diverged, "O"),
            (step.victim_diverged, "V"),
            (step.state_diverged, "S"),
        )
        if active
    )
    lane_summary = " ".join(
        f"{badge.policy}:{badge.decision_code}" for badge in badges
    )
    short_summary = (
        f"{lane_summary} | {divergence_codes}"
        if divergence_codes
        else lane_summary
    )
    lane_lines = "\n".join(
        f"{badge.policy}: {badge.cache_status}; "
        f"{badge.decision_kind.value}; hit way={badge.hit_way}; "
        f"fill way={badge.fill_way}; victim way={badge.victim_way}"
        for badge in badges
    )
    divergence_lines = "\n".join(
        (
            f"Outcome divergence: {step.outcome_diverged}",
            f"Victim divergence: {step.victim_diverged}",
            f"State divergence: {step.state_diverged}",
        )
    )
    return PolicyTimelineItemViewModel(
        step_index=step.step_index,
        address=step.address,
        address_hex=step.address_hex,
        block_address=step.block_address,
        set_index=step.set_index,
        tag=step.tag,
        lane_badges=badges,
        outcome_diverged=step.outcome_diverged,
        victim_diverged=step.victim_diverged,
        state_diverged=step.state_diverged,
        is_current=step.step_index == current_step_index,
        is_selected=step.step_index == selected_step_index,
        short_summary=short_summary,
        tooltip=(
            f"Step {step.step_index + 1}\n"
            f"Address: {step.address} ({step.address_hex})\n"
            f"Block: {step.block_address}; Set: {step.set_index}; Tag: {step.tag}\n"
            f"{lane_lines}\n{divergence_lines}"
        ),
    )


__all__ = [
    "PolicyTimelineLaneBadgeViewModel",
    "PolicyTimelineItemViewModel",
    "build_timeline_item",
    "build_timeline_items",
]
