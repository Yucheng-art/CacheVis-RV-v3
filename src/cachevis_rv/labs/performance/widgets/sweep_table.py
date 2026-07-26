"""Read-only sweep comparison table backed by point view models."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem


HEADERS = (
    "Label", "X", "Cache", "Block", "Ways", "Policy", "Hit Time",
    "Effective Penalty", "Hits", "Misses", "Hit Rate", "Total Cycles",
    "AMAT", "Bytes", "Stall Fraction", "AMAT Δ", "Cycle Δ", "Speedup",
    "Baseline", "Best AMAT", "Best Hit Rate", "Lowest Traffic",
)


def display(value) -> str:
    return "N/A" if value is None else str(value)


class SweepTable(QTableWidget):
    point_selected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(0, len(HEADERS), parent)
        self.setObjectName("PerformanceSweepTable")
        self.setHorizontalHeaderLabels(HEADERS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setMinimumHeight(230)
        self._point_ids: list[str] = []
        self.cellClicked.connect(self._select_row)

    def render(self, points) -> None:
        self.blockSignals(True)
        self.setRowCount(len(points))
        self._point_ids = []
        for row, point in enumerate(points):
            self._point_ids.append(point.point_id)
            metrics = point.metrics
            values = (
                point.label, point.x_value, point.config.cache_size_bytes,
                point.config.block_size_bytes, point.config.ways,
                point.config.replacement_policy, point.timing.hit_time_cycles,
                metrics.effective_miss_penalty_cycles, metrics.hits, metrics.misses,
                metrics.hit_rate, metrics.total_cycles, metrics.amat_cycles,
                metrics.bytes_fetched, metrics.miss_stall_fraction,
                point.amat_delta_vs_baseline, point.total_cycles_delta_vs_baseline,
                point.speedup_vs_baseline, "BASELINE" if point.is_baseline else "",
                "BEST" if point.is_best_amat else "", "BEST HIT RATE" if point.is_best_hit_rate else "",
                "LOWEST" if point.is_lowest_traffic else "",
            )
            for column, value in enumerate(values):
                self.setItem(row, column, QTableWidgetItem(display(value)))
            if point.is_selected:
                self.selectRow(row)
        self.resizeColumnsToContents()
        self.blockSignals(False)

    def _select_row(self, row: int, _column: int) -> None:
        if 0 <= row < len(self._point_ids):
            self.point_selected.emit(self._point_ids[row])


__all__ = ["SweepTable", "display"]
