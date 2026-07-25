"""Scrollable product home page for the V3 learning platform."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .lab_registry import AVAILABLE, LabDefinition, get_lab, get_labs


class HomePage(QScrollArea):
    """Present the learning path and all available/future lab cards."""

    navigation_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HomePage")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._action_buttons: dict[str, QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        content = QWidget()
        content.setObjectName("HomePageContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(20)

        eyebrow = QLabel("CACHEVIS-RV / PLATFORM HOME")
        eyebrow.setProperty("role", "muted")
        eyebrow.setStyleSheet("font-size: 11px; font-weight: 800; letter-spacing: 2px;")
        layout.addWidget(eyebrow)

        title = QLabel("CacheVis-RV")
        title.setStyleSheet("font-size: 34px; font-weight: 800;")
        layout.addWidget(title)

        subtitle = QLabel("Interactive Cache Learning Platform")
        subtitle.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(subtitle)

        introduction = QLabel("面向计算机组成与 RISC-V Cache 教学的交互式实验平台。")
        introduction.setProperty("role", "muted")
        introduction.setStyleSheet("font-size: 14px;")
        introduction.setWordWrap(True)
        layout.addWidget(introduction)

        layout.addWidget(self._build_learning_path())

        section_title = QLabel("Explore Labs")
        section_title.setStyleSheet("font-size: 22px; font-weight: 750; margin-top: 8px;")
        layout.addWidget(section_title)

        section_note = QLabel(
            "Start with address mapping, continue through guided cache concepts, "
            "or use the classic experiment tools."
        )
        section_note.setProperty("role", "muted")
        section_note.setWordWrap(True)
        layout.addWidget(section_note)

        cards = QGridLayout()
        cards.setHorizontalSpacing(16)
        cards.setVerticalSpacing(16)
        for index, lab in enumerate(get_labs()):
            cards.addWidget(self._build_lab_card(lab), index // 2, index % 2)
        cards.setColumnStretch(0, 1)
        cards.setColumnStretch(1, 1)
        layout.addLayout(cards)
        layout.addStretch(1)
        self.setWidget(content)

    def _build_learning_path(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("LabCard")
        row = QHBoxLayout(frame)
        row.setContentsMargins(18, 15, 18, 15)
        row.setSpacing(18)
        steps = (
            ("01", "Decode", "Understand address fields and mapping."),
            ("02", "Observe", "Follow cache state and replacement decisions."),
            ("03", "Experiment", "Compare configurations and explain outcomes."),
        )
        for number, title, detail in steps:
            column = QVBoxLayout()
            number_label = QLabel(number)
            number_label.setProperty("role", "muted")
            number_label.setStyleSheet("font-weight: 800;")
            column.addWidget(number_label)
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 16px; font-weight: 750;")
            column.addWidget(title_label)
            detail_label = QLabel(detail)
            detail_label.setProperty("role", "muted")
            detail_label.setWordWrap(True)
            column.addWidget(detail_label)
            row.addLayout(column, 1)
        return frame

    def _build_lab_card(self, lab: LabDefinition) -> QFrame:
        card = QFrame()
        card.setObjectName("LabCard")
        card.setMinimumHeight(220)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(9)

        heading = QHBoxLayout()
        title = QLabel(lab.title)
        title.setStyleSheet("font-size: 17px; font-weight: 750;")
        heading.addWidget(title, 1)
        status = QLabel(lab.status)
        status.setProperty("status", lab.status)
        heading.addWidget(status, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(heading)

        category = QLabel(lab.category.upper())
        category.setProperty("role", "muted")
        category.setStyleSheet("font-size: 10px; font-weight: 800;")
        layout.addWidget(category)

        description = QLabel(lab.description)
        description.setProperty("role", "muted")
        description.setWordWrap(True)
        layout.addWidget(description)

        concepts = QLabel("Concepts: " + " · ".join(lab.concepts))
        concepts.setWordWrap(True)
        concepts.setProperty("role", "muted")
        layout.addWidget(concepts)
        layout.addStretch(1)

        action = QPushButton("Open Lab" if lab.status == AVAILABLE else "Coming Soon")
        action.setEnabled(lab.status == AVAILABLE)
        action.setCursor(Qt.CursorShape.PointingHandCursor)
        action.clicked.connect(
            lambda _checked=False, target=lab.lab_id: self.request_lab(target)
        )
        self._action_buttons[lab.lab_id] = action
        layout.addWidget(action, 0, Qt.AlignmentFlag.AlignLeft)
        return card

    def request_lab(self, lab_id: str) -> bool:
        """Request navigation only when the registry marks a lab available."""
        lab = get_lab(lab_id)
        if lab is None or lab.status != AVAILABLE or lab.factory is None:
            return False
        self.navigation_requested.emit(lab_id)
        return True


__all__ = ["HomePage"]
