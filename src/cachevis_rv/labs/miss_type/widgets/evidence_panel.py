"""Classification evidence chain presentation."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..evidence_view_model import MissTypeEvidenceViewModel


_EVIDENCE_STYLES = {
    "Cache Hit": ("#d9f7df", "#65a873", "#14532d"),
    "Compulsory Miss": ("#e3edff", "#7d9fd0", "#173f73"),
    "Conflict Miss": ("#ffe5c2", "#d38a36", "#713600"),
    "Capacity Miss": ("#ffe1e1", "#d77a7a", "#7f1d1d"),
}


class EvidencePanel(QFrame):
    """Render selected evidence without changing cache or cumulative state."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MissTypeEvidencePanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Classification Evidence")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.historical_hint = QLabel(
            "Selecting a historical step updates evidence only; "
            "cache state remains at the latest execution."
        )
        self.historical_hint.setWordWrap(True)
        self.historical_hint.setProperty("role", "muted")
        layout.addWidget(self.historical_hint)
        self.card = QFrame()
        self.card.setObjectName("MissTypeEvidenceCard")
        card_layout = QVBoxLayout(self.card)
        self.title_label = QLabel("Awaiting first access")
        self.title_label.setObjectName("MissTypeClassificationTitle")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 800;")
        card_layout.addWidget(self.title_label)
        self.facts_label = QLabel("Seen before: —\nActual Cache: —\nReference Cache: —")
        card_layout.addWidget(self.facts_label)
        self.reason_label = QLabel("Run an access to see the complete 3C evidence chain.")
        self.reason_label.setWordWrap(True)
        card_layout.addWidget(self.reason_label)
        self.rule_path_label = QLabel()
        self.rule_path_label.setObjectName("MissTypeRulePath")
        self.rule_path_label.setWordWrap(True)
        card_layout.addWidget(self.rule_path_label)
        layout.addWidget(self.card)

    def render(self, evidence: MissTypeEvidenceViewModel | None) -> None:
        if evidence is None:
            self.title_label.setText("Awaiting first access")
            self.facts_label.setText(
                "Seen before: —\nActual Cache: —\nReference Cache: —"
            )
            self.reason_label.setText(
                "Run an access to see the complete 3C evidence chain."
            )
            self.rule_path_label.clear()
            self._apply_style("#f3f4f6", "#cbd5e1", "#374151")
            return
        self.title_label.setText(evidence.classification_title)
        self.facts_label.setText(
            f"Seen before: {'Yes' if evidence.seen_before else 'No'}\n"
            f"Actual Cache: {evidence.actual_status.upper()}\n"
            f"Reference Cache: {evidence.reference_status.upper()}"
        )
        self.reason_label.setText(evidence.classification_reason)
        self.rule_path_label.setText("\n↓\n".join(evidence.rule_path))
        self._apply_style(*_EVIDENCE_STYLES[evidence.classification_title])

    def _apply_style(self, background: str, border: str, text: str) -> None:
        self.card.setStyleSheet(
            "QFrame#MissTypeEvidenceCard {"
            f"background: {background}; border: 1px solid {border};"
            "border-radius: 8px; }"
            f"QFrame#MissTypeEvidenceCard QLabel {{ color: {text}; }}"
        )
