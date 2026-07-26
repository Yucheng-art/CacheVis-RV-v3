"""Horizontally scrollable selected decision comparison."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from ..decision_view_model import PolicyComparisonEvidenceViewModel
from .policy_lane_panel import PolicyLanePanel


class DecisionPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyDecisionPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Selected Decision Evidence / Historical Selection")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        hint = QLabel(
            "Timeline selection updates these decisions only. Latest Cache State, "
            "Statistics, and Divergence Summary do not roll back."
        )
        hint.setWordWrap(True)
        hint.setProperty("role", "muted")
        layout.addWidget(hint)
        self.summary_label = QLabel("Awaiting first access")
        self.summary_label.setObjectName("PolicySelectedDecisionSummary")
        layout.addWidget(self.summary_label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        row = QHBoxLayout(content)
        self.lane_panels = {
            policy: PolicyLanePanel(policy) for policy in ("LRU", "FIFO", "Random")
        }
        for panel in self.lane_panels.values():
            row.addWidget(panel, 1)
        content.setMinimumWidth(980)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)

    def render(self, model: PolicyComparisonEvidenceViewModel | None) -> None:
        if model is None:
            self.summary_label.setText("Awaiting first access")
            for panel in self.lane_panels.values():
                panel.render(None)
            return
        self.summary_label.setText(
            f"Selected step {model.step_index + 1} · {model.address_hex} · "
            f"Block {model.block_address} · Set {model.set_index} · Tag {model.tag} · "
            f"{model.divergence_title}"
        )
        by_policy = {lane.policy: lane for lane in model.lane_decisions}
        for policy, panel in self.lane_panels.items():
            panel.render(by_policy[policy])


__all__ = ["DecisionPanel"]
