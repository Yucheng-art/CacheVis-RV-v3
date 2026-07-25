"""Step Summary panel for selected timeline chips."""

from PySide6.QtWidgets import QGroupBox, QTextEdit, QVBoxLayout, QWidget

from step_summary_view_model import build_step_summary
from visualizer_model import AccessStepViewModel


class StepSummaryWidget(QGroupBox):
    """Displays a summary-only view of one selected timeline step."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Step Summary", parent)
        self.setMaximumHeight(180)
        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setMinimumHeight(90)
        self._text.setMaximumHeight(135)
        layout.addWidget(self._text)

    def set_step(self, step: AccessStepViewModel) -> None:
        """Show a selected step summary without changing cache state."""
        summary = build_step_summary(step)
        self._text.setPlainText("\n".join(summary.summary_lines))

    def clear(self) -> None:
        """Reset the panel to its placeholder state."""
        self._text.setPlainText("Select a timeline step to inspect its summary.")
