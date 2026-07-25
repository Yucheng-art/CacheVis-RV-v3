"""Horizontally scrollable Miss Type timeline."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..timeline_view_model import MissTypeTimelineItemViewModel


_CHIP_COLORS = {
    "H": ("#d9f7df", "#65a873", "#14532d"),
    "C": ("#e3edff", "#7d9fd0", "#173f73"),
    "F": ("#ffe5c2", "#d38a36", "#713600"),
    "A": ("#ffe1e1", "#d77a7a", "#7f1d1d"),
}


class MissTypeTimeline(QFrame):
    """Emit selected step indexes while rendering timeline view models."""

    step_selected = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MissTypeTimeline")
        layout = QVBoxLayout(self)
        heading = QLabel("Timeline")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.empty_label = QLabel("No accesses yet.")
        self.empty_label.setProperty("role", "muted")
        layout.addWidget(self.empty_label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setMinimumHeight(130)
        self.content = QWidget()
        self.row = QHBoxLayout(self.content)
        self.row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

    def render(self, items: tuple[MissTypeTimelineItemViewModel, ...]) -> None:
        while self.row.count():
            item = self.row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.empty_label.setVisible(not items)
        self.scroll.setVisible(bool(items))
        for item in items:
            self.row.addWidget(self._chip(item))
        self.row.addStretch(1)

    def _chip(self, item: MissTypeTimelineItemViewModel) -> QPushButton:
        badges = []
        if item.is_current:
            badges.append("CURRENT")
        if item.is_selected:
            badges.append("SELECTED")
        badge_text = "\n" + " · ".join(badges) if badges else ""
        chip = QPushButton(
            f"Step {item.step_number}\n{item.address_hex}\n"
            f"Block {item.block_address} · {item.result_code}{badge_text}"
        )
        chip.setObjectName(f"MissTypeTimelineStep_{item.step_index}")
        chip.setMinimumWidth(135)
        chip.setMinimumHeight(86)
        chip.setToolTip("\n".join(item.tooltip_lines))
        background, border, text = _CHIP_COLORS[item.result_code]
        selected_border = "#334155" if item.is_selected else border
        chip.setStyleSheet(
            f"QPushButton {{ background: {background}; color: {text};"
            f" border: 2px solid {selected_border}; border-radius: 7px;"
            " padding: 7px; text-align: left; font-weight: 650; }"
        )
        chip.clicked.connect(
            lambda _checked=False, index=item.step_index: self.step_selected.emit(index)
        )
        return chip
