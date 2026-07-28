"""Presentation-neutral lane decision models."""

from dataclasses import dataclass

from .model import WritePolicyDecisionEvidence
from .traffic_view_model import WritePolicyTrafficViewModel, build_traffic_view_model


@dataclass(frozen=True)
class WritePolicyLaneDecisionViewModel:
    lane_id: str
    lane_label: str
    write_policy: str
    write_allocate: bool
    access_kind: str
    address: int
    address_hex: str
    result_label: str
    decision_kind: str
    cache_hit: bool
    allocated: bool
    bypassed: bool
    hit_way: int | None
    fill_way: int | None
    evicted_way: int | None
    victim_tag: int | None
    victim_dirty: bool
    line_dirty_before: bool | None
    line_dirty_after: bool | None
    traffic: WritePolicyTrafficViewModel
    classification_reason: str
    rule_path: tuple[str, ...]
    metadata_consistent: bool


def build_lane_decision_view_model(
    evidence: WritePolicyDecisionEvidence,
) -> WritePolicyLaneDecisionViewModel:
    if not isinstance(evidence, WritePolicyDecisionEvidence):
        raise ValueError("evidence must be WritePolicyDecisionEvidence")
    return WritePolicyLaneDecisionViewModel(
        lane_id=evidence.lane.lane_id,
        lane_label=evidence.lane.label,
        write_policy=evidence.lane.write_policy,
        write_allocate=evidence.lane.write_allocate,
        access_kind=evidence.access.kind.value,
        address=evidence.access.address,
        address_hex=f"0x{evidence.access.address:x}",
        result_label="HIT" if evidence.cache_hit else "MISS",
        decision_kind=evidence.decision_kind.value,
        cache_hit=evidence.cache_hit,
        allocated=evidence.allocated,
        bypassed=evidence.bypassed,
        hit_way=evidence.hit_way,
        fill_way=evidence.fill_way,
        evicted_way=evidence.evicted_way,
        victim_tag=evidence.victim_tag,
        victim_dirty=evidence.victim_dirty,
        line_dirty_before=evidence.line_dirty_before,
        line_dirty_after=evidence.line_dirty_after,
        traffic=build_traffic_view_model(evidence.traffic_delta),
        classification_reason=evidence.classification_reason,
        rule_path=evidence.rule_path,
        metadata_consistent=evidence.metadata_consistent,
    )


__all__ = ["WritePolicyLaneDecisionViewModel", "build_lane_decision_view_model"]
