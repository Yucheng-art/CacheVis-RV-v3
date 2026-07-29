from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from .common import section_frame, value_text


class TimelinePanel(QWidget):
    step_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Timeline")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        headers = ["Step", "R/W", "Address", "Outcome", "Allocation", "Bypass", "Writeback", "Traffic", "Dirty", "Cache"]
        for lane in ("WT+WA", "WT+NWA", "WB+WA", "WB+NWA"):
            headers.append(f"{lane} Step/Runtime/Drain B")
        headers.extend(("Selected", "Latest"))
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(240)
        self.table.cellClicked.connect(self._cell_clicked)
        layout.addWidget(self.table)
        self._step_indices = ()

    def _cell_clicked(self, row, _column):
        if 0 <= row < len(self._step_indices): self.step_selected.emit(self._step_indices[row])

    def render(self, models):
        self._step_indices = tuple(model.step_index for model in models)
        self.table.setRowCount(len(models))
        for row, model in enumerate(models):
            values = [model.display_step_number, model.access_kind.upper(), model.address_hex,
                      model.outcome_diverged, model.allocation_diverged, model.bypass_diverged,
                      model.writeback_diverged, model.traffic_diverged,
                      model.dirty_state_diverged, model.cache_state_diverged]
            values.extend(f"{traffic.step_total_bytes}/{traffic.cumulative_runtime_bytes}/{traffic.cumulative_with_final_drain_bytes}" for traffic in model.lane_traffic)
            values.extend((model.is_selected, model.is_latest))
            for column, value in enumerate(values): self.table.setItem(row, column, QTableWidgetItem(value_text(value)))
            if model.is_selected: self.table.selectRow(row)
        self.table.resizeColumnsToContents()


__all__ = ["TimelinePanel"]
