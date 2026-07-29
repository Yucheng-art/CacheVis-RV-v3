from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from .common import section_frame, value_text


COLUMNS = (
    ("Lane", "lane_label"), ("Accesses", "accesses"), ("Reads", "reads"), ("Writes", "writes"),
    ("Hits", "hits"), ("Misses", "misses"), ("Hit Rate", "hit_rate"),
    ("Read H/M", None), ("Write H/M", None), ("Write Miss Alloc", "write_miss_allocations"),
    ("Write Miss Bypass", "write_miss_bypasses"), ("Block Fills", "block_fills"),
    ("Clean Evictions", "clean_evictions"), ("Dirty Evictions", "dirty_evictions"),
    ("Immediate Stores", "immediate_store_writes"), ("Bypass Writes", "bypass_writes"),
    ("Dirty Writebacks", "dirty_writebacks"), ("Read Tx/B", None), ("Write Tx/B", None),
    ("Total Tx/B", None), ("Final Dirty L/B", None), ("Write B + Drain", "memory_write_bytes_with_final_drain"),
    ("Total B + Drain", "total_lower_memory_bytes_with_final_drain"), ("Access Inv", "access_partition_ok"),
    ("Read Inv", "read_partition_ok"), ("Write Inv", "write_partition_ok"),
    ("Write Miss Inv", "write_miss_partition_ok"), ("Fill Inv", "fill_relation_ok"),
    ("Dirty WB Inv", "dirty_writeback_relation_ok"), ("Runtime Inv", "runtime_traffic_relation_ok"),
    ("Drain Inv", "final_drain_relation_ok"),
)


class StatisticsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Current Cumulative Statistics")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(tuple(label for label, _ in COLUMNS))
        self.table.setMinimumHeight(210); layout.addWidget(self.table)

    def render(self, models):
        self.table.setRowCount(len(models))
        for row, model in enumerate(models):
            special = {
                7: f"{model.read_hits}/{model.read_misses}", 8: f"{model.write_hits}/{model.write_misses}",
                17: f"{model.memory_read_transactions}/{model.memory_read_bytes}",
                18: f"{model.memory_write_transactions}/{model.memory_write_bytes}",
                19: f"{model.total_lower_memory_transactions}/{model.total_lower_memory_bytes}",
                20: f"{model.final_dirty_lines}/{model.final_dirty_bytes}",
            }
            for column, (_label, attribute) in enumerate(COLUMNS):
                value = special.get(column, getattr(model, attribute) if attribute else "")
                if attribute == "hit_rate": value = f"{value:.1%}"
                self.table.setItem(row, column, QTableWidgetItem(value_text(value)))
        self.table.resizeColumnsToContents()


__all__ = ["StatisticsPanel"]
