from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from .common import section_frame
from .traffic_canvas import TrafficCanvas


class TrafficPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Traffic Comparison")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        note = QLabel("Final dirty drain is an analytical value, not an extra trace step; it does not mutate the Cache. Runtime and with-drain leaders may differ, and ties are retained.")
        note.setWordWrap(True); note.setStyleSheet("color: #a9bad0;"); layout.addWidget(note)
        self.canvas = TrafficCanvas(); layout.addWidget(self.canvas)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(("Lane", "Read B", "Write B", "Runtime Total B", "Final Dirty B", "With Drain B", "Runtime Tx", "With Drain Write B"))
        self.table.setMinimumHeight(180); layout.addWidget(self.table)

    def render(self, models):
        self.canvas.render(models)
        self.table.setRowCount(len(models))
        for row, model in enumerate(models):
            values = (model.lane_label, model.memory_read_bytes, model.memory_write_bytes,
                      model.total_lower_memory_bytes, model.final_dirty_bytes,
                      model.total_lower_memory_bytes_with_final_drain,
                      model.total_lower_memory_transactions,
                      model.memory_write_bytes_with_final_drain)
            for column, value in enumerate(values): self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()


__all__ = ["TrafficPanel"]
