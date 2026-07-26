"""Presentation-ready locality evidence derived from completed steps."""

from dataclasses import dataclass

from .model import LocalityKind, LocalityStep


@dataclass(frozen=True)
class LocalityEvidenceViewModel:
    locality_kind: LocalityKind
    classification_title: str
    classification_reason: str
    rule_path: tuple[str, ...]
    address_seen_before: bool
    block_seen_before: bool
    offset_seen_before: bool
    previous_address_step: int | None
    previous_block_step: int | None
    address_reuse_gap: int | None
    block_reuse_gap: int | None
    block_reuse_distance: int | None
    same_block_as_previous: bool
    address_delta: int | None
    cache_status: str
    teaching_insight: str


def build_evidence_view_model(step: LocalityStep) -> LocalityEvidenceViewModel:
    """Translate authoritative locality evidence without reclassification."""
    evidence = step.evidence
    if step.locality_kind is LocalityKind.FIRST_TOUCH:
        title = "First Touch"
        path = (
            "Memory block not seen before",
            "First Touch",
            "Cache result is independent evidence",
        )
        insight = (
            "A first touch describes trace history; it may be a cache hit or miss "
            "depending on cache state."
        )
    elif step.locality_kind is LocalityKind.SPATIAL:
        title = "Spatial Locality"
        path = (
            "Address not seen before",
            "Memory block seen before",
            "Spatial Locality",
        )
        insight = (
            "Spatial locality means a new address reuses an observed block; "
            "cache hit or miss is reported separately."
        )
    else:
        title = "Temporal Locality"
        path = (
            "Exact address seen before",
            "Temporal Locality",
        )
        insight = (
            "Temporal locality means exact-address reuse; it does not guarantee "
            "that the cache still contains the block."
        )
    return LocalityEvidenceViewModel(
        locality_kind=step.locality_kind,
        classification_title=title,
        classification_reason=evidence.classification_reason,
        rule_path=path,
        address_seen_before=evidence.address_seen_before,
        block_seen_before=evidence.block_seen_before,
        offset_seen_before=evidence.offset_seen_before,
        previous_address_step=evidence.previous_address_step,
        previous_block_step=evidence.previous_block_step,
        address_reuse_gap=evidence.address_reuse_gap,
        block_reuse_gap=evidence.block_reuse_gap,
        block_reuse_distance=evidence.block_reuse_distance,
        same_block_as_previous=evidence.same_block_as_previous,
        address_delta=evidence.address_delta,
        cache_status="Hit" if step.cache_hit else "Miss",
        teaching_insight=insight,
    )


__all__ = ["LocalityEvidenceViewModel", "build_evidence_view_model"]
