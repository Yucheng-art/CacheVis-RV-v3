"""Card-based Cache Contents visualization for Address Visualizer."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ..model import CacheLineViewModel
from ..view_models.cache_contents import (
    CacheLineCardViewModel,
    build_cache_line_card_models,
)


CARD_STYLES = {
    "hit": ("#d8f7d4", "#248a35"),
    "invalid_fill": ("#fff3bf", "#b08300"),
    "victim": ("#ffe2bd", "#b35a00"),
    "current_set": ("#e3efff", "#2d63ad"),
    "empty": ("#f4f4f4", "#999999"),
    "normal": ("#ffffff", "#bbbbbb"),
}


class CacheContentsWidget(QWidget):
    """Scrollable set/way card view for cache contents."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows_layout: QVBoxLayout | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        hint = QLabel(
            "Rows are cache sets selected by Index. Cards are ways inside each set. "
            "Metadata shows the replacement state used by LRU/FIFO."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.StyledPanel)
        self._container = QWidget()
        self._rows_layout = QVBoxLayout(self._container)
        self._rows_layout.setContentsMargins(8, 8, 8, 8)
        self._rows_layout.setSpacing(8)
        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

    def clear(self) -> None:
        """Clear all visible cache rows."""
        self._clear_rows()

    def set_cache_snapshot(
        self,
        snapshot: list[list[CacheLineViewModel]],
        *,
        mapped_set: int | None,
        hit_way: int | None,
        victim_way: int | None,
        replacement_reason: str | None,
    ) -> None:
        """Render a cache snapshot as set rows and way cards."""
        self._clear_rows()
        if self._rows_layout is None:
            return

        rows = build_cache_line_card_models(
            snapshot,
            mapped_set=mapped_set,
            hit_way=hit_way,
            victim_way=victim_way,
            replacement_reason=replacement_reason,
        )
        if not rows:
            self._rows_layout.addWidget(QLabel("Cache is empty."))
            self._rows_layout.addStretch(1)
            return

        for set_index, cache_set in enumerate(rows):
            row = self._build_set_row(set_index, cache_set, mapped_set)
            self._rows_layout.addWidget(row)
        self._rows_layout.addStretch(1)

    def _build_set_row(
        self,
        set_index: int,
        cards: list[CacheLineCardViewModel],
        mapped_set: int | None,
    ) -> QFrame:
        row_frame = QFrame()
        row_frame.setFrameShape(QFrame.Shape.StyledPanel)
        row_frame.setStyleSheet(_row_style(mapped_set == set_index))
        row_layout = QVBoxLayout(row_frame)
        row_layout.setContentsMargins(8, 6, 8, 8)
        row_layout.setSpacing(6)

        title = QLabel(f"Set {set_index}" + ("  CURRENT SET" if mapped_set == set_index else ""))
        title.setStyleSheet("font-weight: bold;")
        row_layout.addWidget(title)

        ways = QHBoxLayout()
        ways.setSpacing(8)
        for card in cards:
            ways.addWidget(_build_way_card(card))
        ways.addStretch(1)
        row_layout.addLayout(ways)
        return row_frame

    def _clear_rows(self) -> None:
        if self._rows_layout is None:
            return
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


def _build_way_card(card: CacheLineCardViewModel) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setMinimumWidth(150)
    frame.setToolTip(card.tooltip)
    frame.setStyleSheet(_card_style(card.style_role))

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 6, 8, 6)
    layout.setSpacing(3)

    title = QLabel(f"Way {card.way_index}")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-weight: bold;")
    layout.addWidget(title)

    if card.markers:
        marker = QLabel(" / ".join(card.markers))
        marker.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marker.setWordWrap(True)
        marker.setStyleSheet("font-weight: bold;")
        layout.addWidget(marker)

    for label, value in (
        ("valid", card.valid_text),
        ("tag", card.tag_text),
        ("dirty", card.dirty_text),
        ("last_used", card.last_used_text),
        ("insert_time", card.insert_time_text),
    ):
        field = QLabel(f"{label}: {value}")
        field.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(field)
    return frame


def _card_style(role: str) -> str:
    bg, border = CARD_STYLES.get(role, CARD_STYLES["normal"])
    return (
        "QFrame {"
        f"background-color: {bg};"
        f"border: 2px solid {border};"
        "border-radius: 6px;"
        "}"
    )


def _row_style(is_current: bool) -> str:
    if is_current:
        return "QFrame { background-color: #f2f7ff; border: 2px solid #2d63ad; }"
    return "QFrame { background-color: #ffffff; border: 1px solid #cccccc; }"
