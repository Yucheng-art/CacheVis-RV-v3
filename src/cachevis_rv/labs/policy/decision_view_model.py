"""Decision evidence presentation models for Policy Lab."""

from dataclasses import dataclass

from .model import (
    PolicyComparisonStep,
    PolicyDecisionEvidence,
    PolicyDecisionKind,
    PolicyLineSnapshot,
)


@dataclass(frozen=True)
class PolicyLaneDecisionViewModel:
    policy: str
    decision_kind: PolicyDecisionKind
    cache_status: str
    decision_title: str
    classification_reason: str
    rule_path: tuple[str, ...]
    set_index: int
    tag: int
    hit_way: int | None
    fill_way: int | None
    victim_way: int | None
    victim_tag: int | None
    valid_ways_before: tuple[int, ...]
    invalid_ways_before: tuple[int, ...]
    eligible_victim_ways: tuple[int, ...]
    lru_order_before: tuple[int, ...]
    fifo_order_before: tuple[int, ...]
    random_candidate_ways: tuple[int, ...]
    selected_metric_label: str | None
    selected_metric_value: int | None
    random_seed: int | None
    random_draw_index: int | None
    metadata_consistent: bool
    candidate_last_used: tuple[tuple[int, int], ...] = ()
    candidate_insert_times: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class PolicyComparisonEvidenceViewModel:
    step_index: int
    address: int
    address_hex: str
    block_address: int
    set_index: int
    tag: int
    lane_decisions: tuple[PolicyLaneDecisionViewModel, ...]
    outcome_diverged: bool
    victim_diverged: bool
    state_diverged: bool
    divergence_title: str
    teaching_insight: str


def build_lane_decision_view_model(
    evidence: PolicyDecisionEvidence,
    before_set_lines: tuple[PolicyLineSnapshot, ...] = (),
) -> PolicyLaneDecisionViewModel:
    title, path, metric_label = _decision_text(evidence)
    return PolicyLaneDecisionViewModel(
        policy=evidence.policy,
        decision_kind=evidence.decision_kind,
        cache_status=(
            "HIT" if evidence.decision_kind is PolicyDecisionKind.HIT else "MISS"
        ),
        decision_title=title,
        classification_reason=evidence.classification_reason,
        rule_path=path,
        set_index=evidence.set_index,
        tag=evidence.tag,
        hit_way=evidence.hit_way,
        fill_way=evidence.fill_way,
        victim_way=evidence.victim_way,
        victim_tag=evidence.victim_tag,
        valid_ways_before=evidence.valid_ways_before,
        invalid_ways_before=evidence.invalid_ways_before,
        eligible_victim_ways=evidence.eligible_victim_ways,
        lru_order_before=evidence.lru_order_before,
        fifo_order_before=evidence.fifo_order_before,
        random_candidate_ways=evidence.random_candidate_ways,
        selected_metric_label=metric_label,
        selected_metric_value=evidence.selected_metric,
        random_seed=evidence.random_seed,
        random_draw_index=evidence.random_draw_index,
        metadata_consistent=evidence.metadata_consistent,
        candidate_last_used=tuple(
            (line.way, line.last_used)
            for line in before_set_lines
            if line.valid and line.way in evidence.eligible_victim_ways
        ),
        candidate_insert_times=tuple(
            (line.way, line.insert_time)
            for line in before_set_lines
            if line.valid and line.way in evidence.eligible_victim_ways
        ),
    )


def build_comparison_evidence_view_model(
    step: PolicyComparisonStep,
) -> PolicyComparisonEvidenceViewModel:
    lane_decisions = tuple(
        build_lane_decision_view_model(lane.decision, lane.before_set_lines)
        for lane in step.lane_steps
    )
    title, insight = _divergence_text(step)
    return PolicyComparisonEvidenceViewModel(
        step_index=step.step_index,
        address=step.address,
        address_hex=step.address_hex,
        block_address=step.block_address,
        set_index=step.set_index,
        tag=step.tag,
        lane_decisions=lane_decisions,
        outcome_diverged=step.outcome_diverged,
        victim_diverged=step.victim_diverged,
        state_diverged=step.state_diverged,
        divergence_title=title,
        teaching_insight=insight,
    )


def _decision_text(
    evidence: PolicyDecisionEvidence,
) -> tuple[str, tuple[str, ...], str | None]:
    if evidence.decision_kind is PolicyDecisionKind.HIT:
        return (
            "Cache hit",
            (
                "Target tag already exists in the mapped set",
                "Cache HIT",
                "No fill or eviction",
            ),
            None,
        )
    if evidence.decision_kind is PolicyDecisionKind.INVALID_FILL:
        return (
            "Fill an invalid way",
            (
                "Target tag is absent",
                "An invalid way is available",
                "Fill that way",
                "No valid line is evicted",
            ),
            None,
        )
    if evidence.policy == "LRU":
        return (
            "LRU eviction",
            (
                "Target tag is absent",
                "The set is full",
                "Compare last_used metadata",
                "Evict an eligible least-recently-used way",
            ),
            "last_used",
        )
    if evidence.policy == "FIFO":
        return (
            "FIFO eviction",
            (
                "Target tag is absent",
                "The set is full",
                "Compare insert_time metadata",
                "Evict an eligible oldest-inserted way",
            ),
            "insert_time",
        )
    return (
        "Random eviction",
        (
            "Target tag is absent",
            "The set is full",
            "All valid ways are candidates",
            "Seeded random stream selects one candidate",
        ),
        None,
    )


def _divergence_text(step: PolicyComparisonStep) -> tuple[str, str]:
    if step.outcome_diverged:
        return (
            "Hit/miss outcomes diverged",
            "Earlier replacement choices now produce different hit/miss outcomes.",
        )
    if step.victim_diverged:
        return (
            "Victim choices diverged",
            "Policies can change cache state before their hit/miss outcomes differ.",
        )
    if step.state_diverged:
        return (
            "Cache states diverged",
            "The policy lanes now hold different cache contents.",
        )
    return (
        "Policies agree at this step",
        "All policy lanes currently have the same hit/miss outcome.",
    )


__all__ = [
    "PolicyLaneDecisionViewModel",
    "PolicyComparisonEvidenceViewModel",
    "build_lane_decision_view_model",
    "build_comparison_evidence_view_model",
]
