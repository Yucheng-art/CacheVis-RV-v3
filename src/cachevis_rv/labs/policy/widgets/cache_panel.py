"""Three uniform, independently scrollable policy cache panels."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from ..cache_view_model import PolicyCacheLineViewModel, PolicyLaneCacheViewModel


_LINE_STYLES = {
    "hit": ("#d9f7df", "#65a873", "#14532d"),
    "victim": ("#ffe1e1", "#c96a6a", "#6f1d1d"),
    "fill": ("#e8e1ff", "#9a83d1", "#3f2768"),
    "eligible": ("#ffebcc", "#cf923d", "#6f3b00"),
    "current": ("#e1efff", "#77a7dc", "#173f73"),
    "empty": ("#f3f4f6", "#9ca3af", "#4b5563"),
    "normal": ("#ffffff", "#cbd5e1", "#1f2937"),
}


class PolicyCachePanel(QFrame):
    def __init__(self, policy: str, parent=None) -> None:
        super().__init__(parent)
        self.policy = policy
        self.setObjectName(f"PolicyCacheLane_{policy}")
        self.setMinimumWidth(310)
        layout = QVBoxLayout(self)
        self.heading = QLabel(policy)
        self.heading.setStyleSheet("font-size: 18px; font-weight: 850;")
        layout.addWidget(self.heading)
        self.config_label = QLabel("No active session")
        self.config_label.setWordWrap(True)
        layout.addWidget(self.config_label)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(250)
        self.content = QWidget()
        self.lines_layout = QVBoxLayout(self.content)
        self.lines_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        self.line_cards: list[QFrame] = []

    def render(self, lane: PolicyLaneCacheViewModel | None) -> None:
        self._clear()
        if lane is None:
            self.config_label.setText("No active session")
            return
        config = lane.config
        self.config_label.setText(
            f"{config.cache_size_bytes} B cache · {config.block_size_bytes} B block · "
            f"{config.ways} way(s) · {config.sets} set(s)"
        )
        for line in lane.cache_lines:
            card = self._line_card(line)
            self.line_cards.append(card)
            self.lines_layout.addWidget(card)

    def _line_card(self, line: PolicyCacheLineViewModel) -> QFrame:
        role, badges = self._role(line)
        background, border, text = _LINE_STYLES[role]
        card = QFrame()
        card.setObjectName("PolicyCacheLineCard")
        card.setProperty("set_index", line.set_index)
        card.setProperty("way", line.way)
        card.setProperty("badges", tuple(badges))
        card.setStyleSheet(
            "QFrame#PolicyCacheLineCard {"
            f"background: {background}; border: 1px solid {border};"
            "border-radius: 7px; }"
            f"QFrame#PolicyCacheLineCard QLabel {{ color: {text}; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(9, 7, 9, 7)
        title = QLabel(f"Set {line.set_index} · Way {line.way}")
        title.setStyleSheet("font-weight: 800;")
        layout.addWidget(title)
        if badges:
            badge = QLabel(" · ".join(badges))
            badge.setStyleSheet("font-size: 10px; font-weight: 850;")
            layout.addWidget(badge)
        tag = "—" if line.tag is None else f"0x{line.tag:X}"
        facts = QLabel(
            f"Valid: {int(line.valid)}   Tag: {tag}   Dirty: {int(line.dirty)}\n"
            f"Last Used: {line.last_used}   Insert Time: {line.insert_time}"
        )
        if line.tag is not None:
            facts.setToolTip(f"Full tag integer: {line.tag}")
        layout.addWidget(facts)
        return card

    @staticmethod
    def _role(line: PolicyCacheLineViewModel) -> tuple[str, list[str]]:
        badges = []
        if not line.valid:
            badges.append("EMPTY")
        if line.is_current_set:
            badges.append("CURRENT SET")
        if line.is_hit_way:
            badges.append("HIT")
        if line.is_fill_way:
            badges.append("FILL")
        if line.is_victim_way:
            badges.append("VICTIM")
        if line.is_valid_candidate:
            badges.append("VALID CANDIDATE")
        if line.is_eligible_victim:
            badges.append("ELIGIBLE VICTIM")
        if line.is_changed_by_current_access:
            badges.append("CHANGED")
        if line.is_hit_way:
            return "hit", badges
        if line.is_victim_way:
            return "victim", badges
        if line.is_fill_way:
            return "fill", badges
        if line.is_eligible_victim:
            return "eligible", badges
        if line.is_current_set:
            return "current", badges
        if not line.valid:
            return "empty", badges
        return "normal", badges

    def _clear(self) -> None:
        while self.lines_layout.count():
            item = self.lines_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.line_cards = []


class CachePanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyCachePanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Latest Cache State")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        hint = QLabel(
            "These three caches always show the latest execution, even while a "
            "historical decision is selected above."
        )
        hint.setWordWrap(True)
        hint.setProperty("role", "muted")
        layout.addWidget(hint)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        content = QWidget()
        row = QHBoxLayout(content)
        self.lane_panels = {
            policy: PolicyCachePanel(policy) for policy in ("LRU", "FIFO", "Random")
        }
        for panel in self.lane_panels.values():
            row.addWidget(panel, 1)
        content.setMinimumWidth(980)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)

    def render(self, lanes: tuple[PolicyLaneCacheViewModel, ...]) -> None:
        by_policy = {lane.policy: lane for lane in lanes}
        for policy, panel in self.lane_panels.items():
            panel.render(by_policy.get(policy))


__all__ = ["CachePanel", "PolicyCachePanel"]
