"""Selected Locality evidence and teaching chain."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..evidence_view_model import LocalityEvidenceViewModel
from ..model import LocalityKind


_STYLES = {
    LocalityKind.FIRST_TOUCH: ("#e5edf5", "#6f8ba8", "#17324d"),
    LocalityKind.SPATIAL: ("#ece7ff", "#8b75c9", "#3f2768"),
    LocalityKind.TEMPORAL: ("#ffebcc", "#cf923d", "#6f3b00"),
}


class EvidencePanel(QFrame):
    """Render selected evidence without mutating latest execution state."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityEvidencePanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Locality Evidence / Selected Step")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        hint = QLabel(
            "Selecting a historical step updates evidence only; cache, statistics, "
            "and access map remain at the latest execution."
        )
        hint.setWordWrap(True)
        hint.setProperty("role", "muted")
        layout.addWidget(hint)
        self.card = QFrame()
        self.card.setObjectName("LocalityEvidenceCard")
        card_layout = QVBoxLayout(self.card)
        self.title_label = QLabel("Awaiting first access")
        self.title_label.setObjectName("LocalityClassificationTitle")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 800;")
        card_layout.addWidget(self.title_label)
        self.cache_badge = QLabel("CACHE —")
        self.cache_badge.setObjectName("LocalityCacheResultBadge")
        card_layout.addWidget(self.cache_badge)
        self.facts_label = QLabel("No evidence selected.")
        self.facts_label.setWordWrap(True)
        card_layout.addWidget(self.facts_label)
        self.reason_label = QLabel(
            "Run an access to inspect seen-address, seen-block, and reuse evidence."
        )
        self.reason_label.setWordWrap(True)
        card_layout.addWidget(self.reason_label)
        self.rule_path_label = QLabel()
        self.rule_path_label.setObjectName("LocalityRulePath")
        self.rule_path_label.setWordWrap(True)
        card_layout.addWidget(self.rule_path_label)
        self.insight_label = QLabel()
        self.insight_label.setWordWrap(True)
        self.insight_label.setObjectName("LocalityTeachingInsight")
        card_layout.addWidget(self.insight_label)
        layout.addWidget(self.card)
        self.render(None)

    def render(self, evidence: LocalityEvidenceViewModel | None) -> None:
        if evidence is None:
            self.title_label.setText("Awaiting first access")
            self.cache_badge.setText("CACHE —")
            self.facts_label.setText("No evidence selected.")
            self.reason_label.setText(
                "Run an access to inspect seen-address, seen-block, and reuse evidence."
            )
            self.rule_path_label.clear()
            self.insight_label.clear()
            self._apply_style("#f3f4f6", "#cbd5e1", "#374151")
            return
        self.title_label.setText(evidence.classification_title)
        self.cache_badge.setText(f"CACHE {evidence.cache_status.upper()}")
        badge = (
            "background: #d9f7df; color: #14532d;"
            if evidence.cache_status == "Hit"
            else "background: #ffe1e1; color: #7f1d1d;"
        )
        self.cache_badge.setStyleSheet(
            badge + " border-radius: 5px; padding: 4px; font-weight: 800;"
        )
        self.facts_label.setText(
            f"Address seen before: {self._yes_no(evidence.address_seen_before)}\n"
            f"Block seen before: {self._yes_no(evidence.block_seen_before)}\n"
            f"Offset seen before: {self._yes_no(evidence.offset_seen_before)}\n"
            f"Previous address step: {self._value(evidence.previous_address_step)}\n"
            f"Previous block step: {self._value(evidence.previous_block_step)}\n"
            f"Address reuse gap: {self._value(evidence.address_reuse_gap)}\n"
            f"Block reuse gap: {self._value(evidence.block_reuse_gap)}\n"
            f"Block reuse distance: {self._value(evidence.block_reuse_distance)}\n"
            f"Same block as previous: {self._yes_no(evidence.same_block_as_previous)}\n"
            f"Address delta: {self._value(evidence.address_delta)}"
        )
        self.reason_label.setText(evidence.classification_reason)
        self.rule_path_label.setText("\n↓\n".join(evidence.rule_path))
        self.insight_label.setText(evidence.teaching_insight)
        self._apply_style(*_STYLES[evidence.locality_kind])

    def _apply_style(self, background: str, border: str, text: str) -> None:
        self.card.setStyleSheet(
            "QFrame#LocalityEvidenceCard {"
            f"background: {background}; border: 1px solid {border};"
            "border-radius: 8px; }"
            f"QFrame#LocalityEvidenceCard QLabel {{ color: {text}; }}"
        )

    @staticmethod
    def _yes_no(value: bool) -> str:
        return "Yes" if value else "No"

    @staticmethod
    def _value(value) -> str:
        return "N/A" if value is None else str(value)


__all__ = ["EvidencePanel"]
