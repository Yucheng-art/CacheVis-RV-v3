"""Summaries of divergence observed in completed policy steps."""

from dataclasses import dataclass

from .model import PolicyComparisonStep


@dataclass(frozen=True)
class PolicyDivergenceSummaryViewModel:
    has_any_state_divergence: bool
    has_any_victim_divergence: bool
    has_any_outcome_divergence: bool
    first_state_divergence_step: int | None
    first_victim_divergence_step: int | None
    first_outcome_divergence_step: int | None
    state_before_outcome: bool
    divergence_lag_steps: int | None
    latest_outcome_diverged: bool
    latest_victim_diverged: bool
    latest_state_diverged: bool
    summary_title: str
    teaching_insight: str


def build_divergence_summary(
    steps: tuple[PolicyComparisonStep, ...],
) -> PolicyDivergenceSummaryViewModel:
    first_state = _first_step(steps, "state_diverged")
    first_victim = _first_step(steps, "victim_diverged")
    first_outcome = _first_step(steps, "outcome_diverged")
    state_before = (
        first_state is not None
        and first_outcome is not None
        and first_state < first_outcome
    )
    lag = (
        first_outcome - first_state
        if first_state is not None and first_outcome is not None
        else None
    )
    latest = steps[-1] if steps else None
    title, insight = _summary_text(first_state, first_victim, first_outcome)
    return PolicyDivergenceSummaryViewModel(
        has_any_state_divergence=first_state is not None,
        has_any_victim_divergence=first_victim is not None,
        has_any_outcome_divergence=first_outcome is not None,
        first_state_divergence_step=first_state,
        first_victim_divergence_step=first_victim,
        first_outcome_divergence_step=first_outcome,
        state_before_outcome=state_before,
        divergence_lag_steps=lag,
        latest_outcome_diverged=(
            latest.outcome_diverged if latest is not None else False
        ),
        latest_victim_diverged=(
            latest.victim_diverged if latest is not None else False
        ),
        latest_state_diverged=(
            latest.state_diverged if latest is not None else False
        ),
        summary_title=title,
        teaching_insight=insight,
    )


def _first_step(
    steps: tuple[PolicyComparisonStep, ...],
    attribute: str,
) -> int | None:
    return next(
        (step.step_index for step in steps if getattr(step, attribute)),
        None,
    )


def _summary_text(
    first_state: int | None,
    first_victim: int | None,
    first_outcome: int | None,
) -> tuple[str, str]:
    if first_outcome is not None:
        if first_state is not None and first_state < first_outcome:
            return (
                "State diverged before outcomes",
                "Replacement choices changed cache state before a later hit/miss split.",
            )
        return (
            "Hit/miss outcomes have diverged",
            "The policies have produced different observable cache outcomes.",
        )
    if first_state is not None or first_victim is not None:
        return (
            "Internal policy state has diverged",
            "Victim or state divergence is already visible even though outcomes still agree.",
        )
    return (
        "No divergence observed",
        "Only executed steps are summarized; future divergence is not predicted.",
    )


__all__ = [
    "PolicyDivergenceSummaryViewModel",
    "build_divergence_summary",
]
