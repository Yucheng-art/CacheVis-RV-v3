from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from .common import section_frame


class TeachingSummaryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Teaching Summary")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        self.title_label = QLabel("No experiment loaded")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 750;")
        self.description_label = QLabel("Load a preset or edited experiment to begin.")
        self.expected_label = QLabel("N/A")
        self.actual_label = QLabel("N/A")
        self.caution_label = QLabel("N/A")
        for label in (self.description_label, self.expected_label, self.actual_label, self.caution_label):
            label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(QLabel("Expected Teaching Conclusion"))
        layout.addWidget(self.expected_label)
        layout.addWidget(QLabel("Actual Observations"))
        layout.addWidget(self.actual_label)
        layout.addWidget(QLabel("Caution"))
        layout.addWidget(self.caution_label)

    def render(self, state):
        if not state.has_experiment:
            self.title_label.setText("No experiment loaded")
            self.description_label.setText("Load a preset or edited experiment to begin.")
            self.expected_label.setText("N/A")
            self.actual_label.setText("N/A")
            self.caution_label.setText("N/A")
            return
        self.title_label.setText(state.title or "Custom Write Policy Experiment")
        self.description_label.setText(state.description or "")
        self.expected_label.setText(state.expected_teaching_conclusion or "N/A")
        summary = state.comparison_summary
        self.actual_label.setText("\n".join(f"• {item}" for item in summary.actual_observations) or "No accesses have run yet.")
        self.caution_label.setText(summary.caution_note)


__all__ = ["TeachingSummaryPanel"]
