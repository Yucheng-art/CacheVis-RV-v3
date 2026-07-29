from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from .common import section_frame, value_text


FLAGS = (
    ("Outcome", "outcome_divergence_steps", "first_outcome_divergence_step", "outcome_diverged"),
    ("Allocation", "allocation_divergence_steps", "first_allocation_divergence_step", "allocation_diverged"),
    ("Bypass", "bypass_divergence_steps", "first_bypass_divergence_step", "bypass_diverged"),
    ("Writeback", "writeback_divergence_steps", "first_writeback_divergence_step", "writeback_diverged"),
    ("Traffic", "traffic_divergence_steps", "first_traffic_divergence_step", "traffic_diverged"),
    ("Dirty State", "dirty_state_divergence_steps", "first_dirty_state_divergence_step", "dirty_state_diverged"),
    ("Cache State", "cache_state_divergence_steps", "first_cache_state_divergence_step", "cache_state_diverged"),
)


class DivergencePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Divergence Summary")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        self.summary_label = QLabel("No experiment loaded")
        layout.addWidget(self.summary_label)
        self.table = QTableWidget(7, 4)
        self.table.setHorizontalHeaderLabels(("Category", "Count", "First (0-based / display)", "Selected Step"))
        self.table.setMinimumHeight(250)
        layout.addWidget(self.table)

    def render(self, state):
        summary = state.divergence_summary
        selected = state.selected_step
        if summary is None:
            self.summary_label.setText("No experiment loaded")
        else:
            self.summary_label.setText(
                f"All outcomes agree: {summary.all_outcomes_agree_steps} step(s) | Outcome partition: {'OK' if summary.outcome_partition_ok else 'FAILED'}"
            )
        for row, (name, count_attr, first_attr, selected_attr) in enumerate(FLAGS):
            count = None if summary is None else getattr(summary, count_attr)
            first = None if summary is None else getattr(summary, first_attr)
            first_text = "N/A" if first is None else f"{first} / Step {first + 1}"
            selected_flag = None if selected is None else getattr(selected, selected_attr)
            for column, value in enumerate((name, value_text(count), first_text, value_text(selected_flag))):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()


__all__ = ["DivergencePanel"]
