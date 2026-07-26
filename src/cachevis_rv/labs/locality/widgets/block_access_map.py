"""Scrollable block/offset access map for Locality Lab."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..block_access_view_model import (
    BlockAccessCellViewModel,
    BlockAccessSummaryViewModel,
)


class BlockAccessMap(QFrame):
    """Render stable block rows and visited address cells."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityBlockAccessMap")
        layout = QVBoxLayout(self)
        heading = QLabel("Block / Offset Access Map")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        note = QLabel(
            "Rows are memory blocks; cells are visited addresses ordered by offset. "
            "F/S/T evidence and cache H/M counts are shown separately."
        )
        note.setWordWrap(True)
        note.setProperty("role", "muted")
        layout.addWidget(note)
        self.empty_label = QLabel("No executed addresses yet.")
        self.empty_label.setProperty("role", "muted")
        layout.addWidget(self.empty_label)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("LocalityBlockMapScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(220)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.content = QWidget()
        self.rows = QVBoxLayout(self.content)
        self.rows.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        self.cell_widgets: list[QFrame] = []

    def render(
        self,
        cells: tuple[BlockAccessCellViewModel, ...],
        summaries: tuple[BlockAccessSummaryViewModel, ...],
    ) -> None:
        self._clear()
        self.empty_label.setVisible(not cells)
        self.scroll.setVisible(bool(cells))
        by_block = {
            summary.block_address: [
                cell for cell in cells
                if cell.block_address == summary.block_address
            ]
            for summary in summaries
        }
        for summary in summaries:
            self.rows.addWidget(
                self._block_row(summary, by_block[summary.block_address])
            )
        self.rows.addStretch(1)

    def _block_row(
        self,
        summary: BlockAccessSummaryViewModel,
        cells: list[BlockAccessCellViewModel],
    ) -> QFrame:
        current = any(cell.is_current_block for cell in cells)
        row = QFrame()
        row.setObjectName("LocalityBlockRow")
        border = "#4f46e5" if current else "#cbd5e1"
        row.setStyleSheet(
            "QFrame#LocalityBlockRow { background: #f8fafc;"
            f" border: 2px solid {border}; border-radius: 7px; }}"
            "QFrame#LocalityBlockRow QLabel { color: #243447; }"
        )
        layout = QVBoxLayout(row)
        heading = QLabel(
            f"Block {summary.block_address}"
            f"{' · CURRENT BLOCK' if current else ''}  |  "
            f"Accesses {summary.total_accesses} · Offsets {summary.unique_offsets} · "
            f"H {summary.hit_count} / M {summary.miss_count}"
        )
        heading.setStyleSheet("font-weight: 800; color: #172a3f;")
        layout.addWidget(heading)
        cell_row = QHBoxLayout()
        for cell in cells:
            widget = self._cell(cell)
            self.cell_widgets.append(widget)
            cell_row.addWidget(widget)
        cell_row.addStretch(1)
        layout.addLayout(cell_row)
        return row

    @staticmethod
    def _cell(cell: BlockAccessCellViewModel) -> QFrame:
        card = QFrame()
        card.setObjectName("LocalityBlockCell")
        card.setMinimumWidth(160)
        background = "#dbeafe" if cell.is_current_address else "#ffffff"
        border = "#2563eb" if cell.is_current_address else "#94a3b8"
        card.setStyleSheet(
            "QFrame#LocalityBlockCell {"
            f" background: {background}; border: 2px solid {border};"
            " border-radius: 6px; }"
            "QFrame#LocalityBlockCell QLabel { color: #1e293b; }"
        )
        layout = QVBoxLayout(card)
        marker = " · CURRENT ADDRESS" if cell.is_current_address else ""
        title = QLabel(f"Offset {cell.offset}{marker}")
        title.setStyleSheet("font-weight: 800; color: #172a3f;")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Address: {cell.address} (0x{cell.address:X})"))
        layout.addWidget(
            QLabel(
                f"Accesses: {cell.access_count} · "
                f"H {cell.hit_count} / M {cell.miss_count}"
            )
        )
        layout.addWidget(
            QLabel(
                f"F {cell.first_touch_count} / S {cell.spatial_count} / "
                f"T {cell.temporal_count}"
            )
        )
        layout.addWidget(
            QLabel(f"First step: {cell.first_step + 1} · Last: {cell.last_step + 1}")
        )
        return card

    def _clear(self) -> None:
        while self.rows.count():
            item = self.rows.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.cell_widgets = []


__all__ = ["BlockAccessMap"]
