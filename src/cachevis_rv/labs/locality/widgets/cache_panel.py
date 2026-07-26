"""Scrollable cache-state cards for Locality Lab."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from cachevis_rv.core import CacheConfig

from ..cache_view_model import LocalityCacheLineViewModel


_LINE_STYLES = {
    "empty": ("#f3f4f6", "#9ca3af", "#4b5563"),
    "hit": ("#d9f7df", "#65a873", "#14532d"),
    "victim": ("#ffe5c2", "#d38a36", "#713600"),
    "invalid": ("#e8e1ff", "#9a83d1", "#3f2768"),
    "current": ("#e1efff", "#77a7dc", "#173f73"),
    "normal": ("#ffffff", "#cbd5e1", "#1f2937"),
}


class CachePanel(QFrame):
    """Render detached cache-line models without cache logic."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityCachePanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Cache State / Latest Execution")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.description_label = QLabel("No active session.")
        self.description_label.setProperty("role", "muted")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("LocalityCacheScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(230)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.content = QWidget()
        self.grid = QGridLayout(self.content)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

    def render(
        self,
        config: CacheConfig | None,
        lines: tuple[LocalityCacheLineViewModel, ...],
    ) -> None:
        self._clear()
        if config is None:
            self.description_label.setText("No active session.")
            return
        self.description_label.setText(
            f"{config.cache_size_bytes} B cache · "
            f"{config.block_size_bytes} B block · {config.ways} way(s) · "
            f"{config.sets} set(s) · {config.replacement_policy}"
        )
        columns = max(1, min(config.ways, 4))
        for index, line in enumerate(lines):
            self.grid.addWidget(
                self._line_card(line), index // columns, index % columns
            )

    def _line_card(self, line: LocalityCacheLineViewModel) -> QFrame:
        role, badges = self._semantic_role(line)
        background, border, text = _LINE_STYLES[role]
        card = QFrame()
        card.setObjectName("LocalityCacheLineCard")
        card.setMinimumWidth(150)
        card.setStyleSheet(
            "QFrame#LocalityCacheLineCard {"
            f"background: {background}; border: 1px solid {border};"
            "border-radius: 7px; }"
            f"QFrame#LocalityCacheLineCard QLabel {{ color: {text}; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        heading = QLabel(f"Set {line.set_index} · Way {line.way}")
        heading.setStyleSheet(f"font-weight: 750; color: {text};")
        layout.addWidget(heading)
        if badges:
            badge = QLabel(" · ".join(badges))
            badge.setStyleSheet(
                f"font-size: 10px; font-weight: 800; color: {text};"
            )
            layout.addWidget(badge)
        tag = "—" if line.tag is None else f"0x{line.tag:X}"
        tag_label = QLabel(f"Valid: {int(line.valid)}   Tag: {tag}")
        if line.tag is not None:
            tag_label.setToolTip(f"Full tag integer: {line.tag}")
        layout.addWidget(tag_label)
        layout.addWidget(QLabel(f"Dirty: {int(line.dirty)}"))
        layout.addWidget(QLabel(f"Last Used: {line.last_used}"))
        layout.addWidget(QLabel(f"Insert Time: {line.insert_time}"))
        return card

    @staticmethod
    def _semantic_role(
        line: LocalityCacheLineViewModel,
    ) -> tuple[str, list[str]]:
        badges: list[str] = []
        if not line.valid:
            badges.append("EMPTY")
        if line.is_current_set:
            badges.append("CURRENT SET")
        if line.is_hit_way:
            badges.append("HIT")
        if line.is_victim_way:
            badges.append("VICTIM")
        if line.is_invalid_fill:
            badges.append("INVALID FILL")
        if line.is_hit_way:
            return "hit", badges
        if line.is_victim_way:
            return "victim", badges
        if line.is_invalid_fill:
            return "invalid", badges
        if line.is_current_set:
            return "current", badges
        if not line.valid:
            return "empty", badges
        return "normal", badges

    def _clear(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


__all__ = ["CachePanel"]
