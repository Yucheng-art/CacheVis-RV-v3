"""Structured explanation panel for Address Visualizer."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGroupBox, QLabel, QScrollArea, QVBoxLayout, QWidget

from explanation_sections import ExplanationSection, build_explanation_sections
from visualizer_model import AccessStepViewModel


SECTION_STYLES = {
    "hit": ("#d8f7d4", "#248a35"),
    "miss": ("#ffe0e0", "#b53a3a"),
    "replacement": ("#fff3bf", "#b08300"),
    "warning": ("#fff7d6", "#b08300"),
    "normal": ("#ffffff", "#bbbbbb"),
}


class ExplanationPanelWidget(QGroupBox):
    """Displays explanation text as titled sections."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Structured Explanation", parent)
        self.setMinimumWidth(360)
        self.setMaximumWidth(460)
        self._content_layout: QVBoxLayout | None = None
        self._build_ui()
        self.show_placeholder("Load a preset or click Reset to begin.")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(4, 4, 4, 4)
        self._content_layout.setSpacing(8)
        scroll.setWidget(self._content)
        layout.addWidget(scroll)

    def set_step(self, step: AccessStepViewModel) -> None:
        """Render structured explanation sections for a completed access."""
        self.set_sections(build_explanation_sections(step))

    def set_sections(self, sections: list[ExplanationSection]) -> None:
        """Render prebuilt explanation sections."""
        self._clear()
        if self._content_layout is None:
            return
        for section in sections:
            self._content_layout.addWidget(_build_section_card(section))
        self._content_layout.addStretch(1)

    def show_placeholder(self, text: str) -> None:
        """Show a single neutral message."""
        self._clear()
        if self._content_layout is None:
            return
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._content_layout.addWidget(label)
        self._content_layout.addStretch(1)

    def _clear(self) -> None:
        if self._content_layout is None:
            return
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


def _build_section_card(section: ExplanationSection) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet(_section_style(section.status))
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setSpacing(5)

    title = QLabel(section.title)
    title.setStyleSheet("font-weight: bold;")
    title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    layout.addWidget(title)

    for line in section.lines:
        label = QLabel(line)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)
    return frame


def _section_style(status: str) -> str:
    bg, border = SECTION_STYLES.get(status, SECTION_STYLES["normal"])
    return (
        "QFrame {"
        f"background-color: {bg};"
        f"border: 2px solid {border};"
        "border-radius: 6px;"
        "}"
    )
