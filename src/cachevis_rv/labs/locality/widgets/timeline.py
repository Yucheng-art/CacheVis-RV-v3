"""Horizontally scrollable Locality timeline."""

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

from ..model import LocalityKind
from ..timeline_view_model import LocalityTimelineItemViewModel


_KIND_STYLES = {
    LocalityKind.FIRST_TOUCH: ("#e5edf5", "#6f8ba8", "#17324d"),
    LocalityKind.SPATIAL: ("#ece7ff", "#8b75c9", "#3f2768"),
    LocalityKind.TEMPORAL: ("#ffebcc", "#cf923d", "#6f3b00"),
}


class LocalityTimeline(QFrame):
    """Render independent F/S/T and H/M semantics and emit selections."""

    step_selected = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityTimeline")
        layout = QVBoxLayout(self)
        heading = QLabel("Timeline")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.empty_label = QLabel("No accesses yet.")
        self.empty_label.setProperty("role", "muted")
        layout.addWidget(self.empty_label)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("LocalityTimelineScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setMinimumHeight(145)
        self.content = QWidget()
        self.row = QHBoxLayout(self.content)
        self.row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        self.chips: list[QPushButton] = []

    def render(self, items: tuple[LocalityTimelineItemViewModel, ...]) -> None:
        while self.row.count():
            item = self.row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.chips = []
        self.empty_label.setVisible(not items)
        self.scroll.setVisible(bool(items))
        for item in items:
            chip = self._chip(item)
            self.chips.append(chip)
            self.row.addWidget(chip)
        self.row.addStretch(1)

    def _chip(self, item: LocalityTimelineItemViewModel) -> QPushButton:
        state_badges = []
        if item.is_current:
            state_badges.append("CURRENT")
        if item.is_selected:
            state_badges.append("SELECTED")
        states = "\n" + " · ".join(state_badges) if state_badges else ""
        cache_label = "H" if item.cache_hit else "M"
        chip = QPushButton(
            f"Step {item.step_index + 1}\n{item.address_hex}\n"
            f"Block {item.block_address} · Offset {item.offset}\n"
            f"{item.short_label}   Cache {cache_label}{states}"
        )
        chip.setObjectName(f"LocalityTimelineStep_{item.step_index}")
        chip.setMinimumWidth(150)
        chip.setMinimumHeight(105)
        chip.setToolTip(item.tooltip)
        background, border, text = _KIND_STYLES[item.locality_kind]
        selected_border = "#334155" if item.is_selected else border
        chip.setStyleSheet(
            f"QPushButton {{ background: {background}; color: {text};"
            f" border: 2px solid {selected_border}; border-radius: 7px;"
            " padding: 7px; text-align: left; font-weight: 650; }"
        )
        chip.clicked.connect(
            lambda _checked=False, index=item.step_index:
                self.step_selected.emit(index)
        )
        return chip


__all__ = ["LocalityTimeline"]
