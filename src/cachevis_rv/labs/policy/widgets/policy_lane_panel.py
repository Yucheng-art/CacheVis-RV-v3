"""One policy's selected decision evidence card."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..decision_view_model import PolicyLaneDecisionViewModel
from ..model import PolicyDecisionKind


_DECISION_STYLES = {
    PolicyDecisionKind.HIT: ("#d9f7df", "#65a873", "#14532d"),
    PolicyDecisionKind.INVALID_FILL: ("#e8e1ff", "#9a83d1", "#3f2768"),
    PolicyDecisionKind.EVICTION: ("#ffe5c2", "#d38a36", "#713600"),
}


class PolicyLanePanel(QFrame):
    """Render one formal PolicyLaneDecisionViewModel without domain logic."""

    def __init__(self, policy: str, parent=None) -> None:
        super().__init__(parent)
        self.policy = policy
        self.setObjectName(f"PolicyDecisionLane_{policy}")
        self.setMinimumWidth(310)
        layout = QVBoxLayout(self)
        self.policy_label = QLabel(policy)
        self.policy_label.setStyleSheet("font-size: 18px; font-weight: 850;")
        layout.addWidget(self.policy_label)
        self.status_label = QLabel("Awaiting selected decision")
        self.status_label.setStyleSheet("font-weight: 800;")
        layout.addWidget(self.status_label)
        self.facts_label = QLabel("Run an access to inspect this policy lane.")
        self.facts_label.setWordWrap(True)
        layout.addWidget(self.facts_label)
        self.metadata_label = QLabel()
        self.metadata_label.setObjectName(f"PolicyMetadata_{policy}")
        self.metadata_label.setWordWrap(True)
        layout.addWidget(self.metadata_label)
        rule_heading = QLabel("Rule path")
        rule_heading.setStyleSheet("font-weight: 800;")
        layout.addWidget(rule_heading)
        self.rule_path_label = QLabel()
        self.rule_path_label.setWordWrap(True)
        layout.addWidget(self.rule_path_label)
        self.reason_label = QLabel()
        self.reason_label.setWordWrap(True)
        layout.addWidget(self.reason_label)
        self.render(None)

    def render(self, model: PolicyLaneDecisionViewModel | None) -> None:
        if model is None:
            self.status_label.setText("Awaiting selected decision")
            self.facts_label.setText("Run an access to inspect this policy lane.")
            self.metadata_label.clear()
            self.rule_path_label.clear()
            self.reason_label.clear()
            self._apply_style("#f3f4f6", "#cbd5e1", "#374151")
            return
        self.status_label.setText(
            f"{model.cache_status} · {model.decision_kind.value.replace('_', ' ').upper()}"
        )
        self.facts_label.setText(
            f"Mapped set: {model.set_index}\n"
            f"Target tag: {model.tag}\n"
            f"Hit way: {self._value(model.hit_way)}\n"
            f"Fill way: {self._value(model.fill_way)}\n"
            f"Victim way: {self._value(model.victim_way)}\n"
            f"Victim tag: {self._value(model.victim_tag)}\n"
            f"Valid ways before: {self._ways(model.valid_ways_before)}\n"
            f"Invalid ways before: {self._ways(model.invalid_ways_before)}\n"
            f"Eligible victim ways: {self._ways(model.eligible_victim_ways)}\n"
            f"Metadata consistent: {'Yes' if model.metadata_consistent else 'NO'}"
        )
        self.metadata_label.setText(self._metadata_text(model))
        self.rule_path_label.setText("\n→\n".join(model.rule_path))
        self.reason_label.setText("Reason: " + model.classification_reason)
        self._apply_style(*_DECISION_STYLES[model.decision_kind])

    def _metadata_text(self, model: PolicyLaneDecisionViewModel) -> str:
        if model.policy == "LRU":
            return (
                f"LRU order (LRU → MRU): {self._ways(model.lru_order_before)}"
                + "\nCandidate last_used: "
                + self._candidate_metadata(model.candidate_last_used)
                + "\nSelected last_used: "
                + self._value(model.selected_metric_value)
            )
        if model.policy == "FIFO":
            return (
                f"FIFO order (oldest → newest): {self._ways(model.fifo_order_before)}"
                + "\nCandidate insert_time: "
                + self._candidate_metadata(model.candidate_insert_times)
                + "\nSelected insert_time: "
                + self._value(model.selected_metric_value)
                + "\nA FIFO hit does not refresh insertion order."
            )
        return (
            f"Random candidates: {self._ways(model.random_candidate_ways)}"
            + f"\nSeed: {self._value(model.random_seed)}"
            + f"\nRandom draw index: {self._value(model.random_draw_index)}"
            + "\nSeeded replay selects from all valid candidates; it does not claim priority."
        )

    def _apply_style(self, background: str, border: str, text: str) -> None:
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{ background: {background};"
            f" border: 1px solid {border}; border-radius: 8px; }}"
            f"QFrame#{self.objectName()} QLabel {{ color: {text}; }}"
        )

    @staticmethod
    def _value(value) -> str:
        return "N/A" if value is None else str(value)

    @staticmethod
    def _ways(values: tuple[int, ...]) -> str:
        return "None" if not values else ", ".join(map(str, values))

    @staticmethod
    def _candidate_metadata(values: tuple[tuple[int, int], ...]) -> str:
        if not values:
            return "None"
        return ", ".join(f"way {way} = {value}" for way, value in values)


__all__ = ["PolicyLanePanel"]
