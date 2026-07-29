from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from .common import section_frame, value_text


class _CacheCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WritePolicyCacheCard")
        self.setStyleSheet("QFrame#WritePolicyCacheCard { background: #f2f7fc; color: #19334d; border: 1px solid #8aa7c2; border-radius: 7px; }")
        layout = QVBoxLayout(self)
        self.heading = QLabel("N/A"); self.heading.setStyleSheet("color: #19334d; font-size: 16px; font-weight: 800;")
        self.summary = QLabel("No cache state"); self.summary.setStyleSheet("color: #19334d;")
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(("Set", "Way", "Valid", "Tag", "State", "Last Used", "Insert Time"))
        self.table.setMinimumHeight(160)
        layout.addWidget(self.heading); layout.addWidget(self.summary); layout.addWidget(self.table)

    def render(self, model):
        if model is None:
            self.heading.setText("N/A"); self.summary.setText("No cache state"); self.table.setRowCount(0); return
        self.heading.setText(model.lane_label)
        self.summary.setText(f"Valid {model.valid_line_count} | Clean {model.clean_line_count} | Dirty {model.dirty_line_count} | Dirty bytes {model.dirty_bytes}")
        self.table.setRowCount(len(model.lines))
        for row, line in enumerate(model.lines):
            values = (line.set_index, line.way, value_text(line.valid), line.tag_hex or "N/A", line.state_label, line.last_used, line.insert_time)
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if line.state_label == "DIRTY": item.setToolTip("Dirty resident line; final drain is analytical until eviction.")
                self.table.setItem(row, column, item)
        self.table.resizeColumnsToContents()


class CachePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Current Run State: Four Lane Cache Contents")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        note = QLabel("Always shows the latest run state; historical evidence selection never rewinds these tables.")
        note.setWordWrap(True); note.setStyleSheet("color: #a9bad0;"); layout.addWidget(note)
        grid = QGridLayout(); layout.addLayout(grid)
        self.cards = tuple(_CacheCard() for _ in range(4))
        for index, card in enumerate(self.cards): grid.addWidget(card, index // 2, index % 2)

    def render(self, models):
        for index, card in enumerate(self.cards): card.render(models[index] if index < len(models) else None)


__all__ = ["CachePanel"]
