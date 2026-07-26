"""Horizontally scrollable three-policy timeline."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from ..timeline_view_model import PolicyTimelineItemViewModel


class PolicyTimeline(QFrame):
    step_selected = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyTimeline")
        layout = QVBoxLayout(self)
        heading = QLabel("Timeline")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        legend = QLabel(
            "H = HIT · I = INVALID FILL · E = EVICTION · "
            "O = Outcome divergence · V = Victim divergence · S = State divergence"
        )
        legend.setWordWrap(True)
        legend.setStyleSheet("color: #334155; font-weight: 650;")
        layout.addWidget(legend)
        self.empty_label = QLabel("No accesses yet.")
        self.empty_label.setProperty("role", "muted")
        layout.addWidget(self.empty_label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setMinimumHeight(165)
        self.content = QWidget()
        self.row = QHBoxLayout(self.content)
        self.row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        self.chips: list[QPushButton] = []

    def render(self, items: tuple[PolicyTimelineItemViewModel, ...]) -> None:
        while self.row.count():
            item = self.row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.chips = []
        self.empty_label.setVisible(not items)
        self.scroll.setVisible(bool(items))
        for model in items:
            chip = self._chip(model)
            self.chips.append(chip)
            self.row.addWidget(chip)
        self.row.addStretch(1)

    def _chip(self, model: PolicyTimelineItemViewModel) -> QPushButton:
        markers = []
        if model.is_current:
            markers.append("CURRENT")
        if model.is_selected:
            markers.append("SELECTED")
        marker_text = "\n" + " · ".join(markers) if markers else ""
        chip = QPushButton(
            f"Step {model.step_index + 1}\n{model.address_hex}\n"
            f"Block {model.block_address} · Set {model.set_index} · Tag {model.tag}\n"
            f"{model.short_summary}{marker_text}"
        )
        chip.setObjectName(f"PolicyTimelineStep_{model.step_index}")
        chip.setMinimumWidth(205)
        chip.setMinimumHeight(125)
        chip.setToolTip(model.tooltip)
        if model.outcome_diverged:
            colors = ("#ffe1e1", "#b85c5c", "#6f1d1d")
        elif model.state_diverged or model.victim_diverged:
            colors = ("#ffebcc", "#cf923d", "#6f3b00")
        else:
            colors = ("#e5edf5", "#8ba2ba", "#20364d")
        background, border, text = colors
        selected_border = "#1e293b" if model.is_selected else border
        chip.setStyleSheet(
            f"QPushButton {{ background: {background}; color: {text};"
            f" border: 2px solid {selected_border}; border-radius: 7px;"
            " padding: 7px; text-align: left; font-weight: 650; }"
        )
        chip.clicked.connect(
            lambda _checked=False, index=model.step_index:
                self.step_selected.emit(index)
        )
        return chip


__all__ = ["PolicyTimeline"]
