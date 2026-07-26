"""Editable, horizontally scrollable sweep-point definitions."""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from cachevis_rv.core import CacheConfig

from ..model import PerformanceRunSpec
from ..timing import PerformanceTimingModel


HEADERS = (
    "Point ID",
    "Label",
    "X Value",
    "Cache Size",
    "Block Size",
    "Ways",
    "Policy",
    "Hit Time",
    "Fixed Miss Overhead",
    "Transfer Cycles / Byte",
)


class PointEditor(QWidget):
    """Edit formal run specifications without executing them."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, len(HEADERS))
        self.table.setObjectName("PerformancePointEditorTable")
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setMinimumHeight(190)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.add_button = QPushButton("Add Point")
        self.remove_button = QPushButton("Remove Selected Point")
        self.add_button.clicked.connect(self.add_empty_point)
        self.remove_button.clicked.connect(self.remove_selected_point)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.remove_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

    def load_points(self, points: tuple[PerformanceRunSpec, ...]) -> None:
        self.table.setRowCount(0)
        for point in points:
            self._append_values(
                (
                    point.point_id,
                    point.label,
                    point.x_value,
                    point.config.cache_size_bytes,
                    point.config.block_size_bytes,
                    point.config.ways,
                    point.config.replacement_policy,
                    point.timing.hit_time_cycles,
                    point.timing.fixed_miss_overhead_cycles,
                    point.timing.transfer_cycles_per_byte,
                )
            )
        self.table.resizeColumnsToContents()

    def add_empty_point(self) -> None:
        index = self.table.rowCount() + 1
        self._append_values((f"point_{index}", f"Point {index}", index, 16, 4, 1, "LRU", 1, 20, 0.5))

    def remove_selected_point(self) -> None:
        rows = sorted({item.row() for item in self.table.selectedItems()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def build_points(self) -> tuple[PerformanceRunSpec, ...]:
        points = []
        for row in range(self.table.rowCount()):
            values = [self._text(row, column) for column in range(len(HEADERS))]
            policy = values[6].upper()
            if policy == "RANDOM":
                raise ValueError("Random policy belongs to Policy Lab; Performance sweeps allow only LRU or FIFO")
            if policy not in {"LRU", "FIFO"}:
                raise ValueError("policy must be LRU or FIFO")
            config = CacheConfig(
                cache_size_bytes=int(values[3]),
                block_size_bytes=int(values[4]),
                ways=int(values[5]),
                replacement_policy=policy,
            )
            timing = PerformanceTimingModel(
                float(values[7]), float(values[8]), float(values[9])
            )
            points.append(
                PerformanceRunSpec(
                    values[0].strip(),
                    values[1].strip(),
                    float(values[2]),
                    config,
                    timing,
                )
            )
        return tuple(points)

    def point_ids(self) -> tuple[str, ...]:
        return tuple(self._text(row, 0).strip() for row in range(self.table.rowCount()))

    def _append_values(self, values) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column, value in enumerate(values):
            self.table.setItem(row, column, QTableWidgetItem(str(value)))

    def _text(self, row: int, column: int) -> str:
        item = self.table.item(row, column)
        return "" if item is None else item.text()


__all__ = ["HEADERS", "PointEditor"]
