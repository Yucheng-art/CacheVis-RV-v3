"""Stable teaching text derived from completed Miss Type classification steps."""

from dataclasses import dataclass

from .model import MissType, MissTypeStep


@dataclass(frozen=True)
class MissTypeEvidenceViewModel:
    """Presentation-ready evidence without GUI or styling concerns."""

    seen_before: bool
    actual_status: str
    reference_status: str
    miss_type: MissType | None
    classification_title: str
    classification_reason: str
    rule_path: tuple[str, ...]


def build_evidence_view_model(step: MissTypeStep) -> MissTypeEvidenceViewModel:
    """Build display text from the classifier's already-computed result."""
    if step.actual_result == "hit":
        title = "Cache Hit"
        rule_path = (
            "Actual Cache Hit",
            "No miss classification",
        )
    elif step.miss_type is MissType.COMPULSORY:
        title = "Compulsory Miss"
        rule_path = (
            "First access to this memory block",
            "Compulsory Miss",
        )
    elif step.miss_type is MissType.CONFLICT:
        title = "Conflict Miss"
        rule_path = (
            "This block was seen before",
            "Actual Cache Miss",
            "Fully Associative Reference Hit",
            "Conflict Miss",
        )
    elif step.miss_type is MissType.CAPACITY:
        title = "Capacity Miss"
        rule_path = (
            "This block was seen before",
            "Actual Cache Miss",
            "Fully Associative Reference Miss",
            "Capacity Miss",
        )
    else:
        raise ValueError("completed miss step must have a strict 3C classification")

    return MissTypeEvidenceViewModel(
        seen_before=step.evidence.seen_before,
        actual_status=step.actual_result.title(),
        reference_status=step.reference_result.title(),
        miss_type=step.miss_type,
        classification_title=title,
        classification_reason=step.evidence.classification_reason,
        rule_path=rule_path,
    )


__all__ = ["MissTypeEvidenceViewModel", "build_evidence_view_model"]
