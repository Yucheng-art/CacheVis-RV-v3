"""Chip-based access timeline for Address Visualizer."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ..model import AccessStepViewModel
from ..view_models.timeline import TimelineItemViewModel, build_timeline_item


CHIP_STYLES = {
    "hit": ("#d8f7d4", "#248a35"),
    "miss": ("#ffe0e0", "#b53a3a"),
    "hit_current": ("#d8f7d4", "#1f5fbf"),
    "miss_current": ("#ffe0e0", "#1f5fbf"),
    "hit_selected": ("#d8f7d4", "#7c3aed"),
    "miss_selected": ("#ffe0e0", "#7c3aed"),
    "hit_current_selected": ("#d8f7d4", "#111827"),
    "miss_current_selected": ("#ffe0e0", "#111827"),
}


class AccessTimelineWidget(QGroupBox):
    """Scrollable row of access chips."""

    step_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Access Timeline", parent)
        self._steps: list[AccessStepViewModel] = []
        self._selected_step_index: int | None = None
        self._chips_layout: QHBoxLayout | None = None
        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.StyledPanel)
        scroll.setMaximumHeight(160)

        self._container = QWidget()
        self._chips_layout = QHBoxLayout(self._container)
        self._chips_layout.setContentsMargins(8, 8, 8, 8)
        self._chips_layout.setSpacing(8)
        scroll.setWidget(self._container)
        layout.addWidget(scroll)

    def clear(self) -> None:
        """Clear all timeline chips."""
        self._steps.clear()
        self._selected_step_index = None
        self._rebuild()

    def add_step(self, step: AccessStepViewModel) -> None:
        """Append a step and mark it as the current item."""
        self._steps.append(step)
        self._selected_step_index = step.step_index
        self._rebuild()

    def get_step(self, step_index: int) -> AccessStepViewModel | None:
        """Return the stored step for a timeline selection."""
        for step in self._steps:
            if step.step_index == step_index:
                return step
        return None

    def _rebuild(self) -> None:
        self._clear_chips()
        if self._chips_layout is None:
            return
        if not self._steps:
            label = QLabel("No accesses yet. Click Step or Run All.")
            label.setWordWrap(True)
            self._chips_layout.addWidget(label)
            self._chips_layout.addStretch(1)
            return

        last_index = len(self._steps) - 1
        for index, step in enumerate(self._steps):
            item = build_timeline_item(
                step,
                is_current=index == last_index,
                is_selected=step.step_index == self._selected_step_index,
            )
            chip = _build_chip(item)
            chip.clicked.connect(self._select_step)
            self._chips_layout.addWidget(chip)
        self._chips_layout.addStretch(1)

    def _select_step(self, step_index: int) -> None:
        self._selected_step_index = step_index
        self._rebuild()
        self.step_selected.emit(step_index)

    def _clear_chips(self) -> None:
        if self._chips_layout is None:
            return
        while self._chips_layout.count():
            item = self._chips_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


class _TimelineChip(QFrame):
    """Clickable frame used as a timeline chip."""

    clicked = Signal(int)

    def __init__(self, step_index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._step_index = step_index

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001 - Qt event type
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._step_index)
        super().mouseReleaseEvent(event)


def _build_chip(item: TimelineItemViewModel) -> _TimelineChip:
    frame = _TimelineChip(item.step_index)
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setMinimumWidth(170)
    frame.setCursor(Qt.CursorShape.PointingHandCursor)
    frame.setToolTip("\n".join(item.tooltip_lines))
    frame.setStyleSheet(_chip_style(item))

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 6, 8, 6)
    layout.setSpacing(3)

    for line_index, line in enumerate(item.label.splitlines()):
        label = QLabel(line)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        if line_index == 0 or item.result in line:
            label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
    return frame


def _chip_style(item: TimelineItemViewModel) -> str:
    role = item.result.lower()
    if item.is_current and item.is_selected:
        role = f"{role}_current_selected"
    elif item.is_current:
        role = f"{role}_current"
    elif item.is_selected:
        role = f"{role}_selected"
    bg, border = CHIP_STYLES.get(role, CHIP_STYLES["miss"])
    border_width = 3 if item.is_current or item.is_selected else 2
    return (
        "QFrame {"
        f"background-color: {bg};"
        f"border: {border_width}px solid {border};"
        "border-radius: 6px;"
        "}"
    )
