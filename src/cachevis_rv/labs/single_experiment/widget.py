"""PySide6 widget for the classic Single Experiment lab."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from cachevis_rv.core import CacheConfig
from cachevis_rv.services import ACCESS_LOG_FIELDS

from .controller import SingleExperimentController
from .view_model import SingleExperimentViewModel


TRACE_TYPES = [
    "sequential",
    "stride",
    "random",
    "matrix",
    "conflict",
    "loop-reuse",
    "block-locality",
    "matrix-row",
    "matrix-column",
]


class SingleExperimentWidget(QWidget):
    """Self-contained classic single-experiment page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = SingleExperimentController()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(12)
        layout.addWidget(self._build_config_panel(), 0)
        layout.addWidget(self._build_results_panel(), 1)

    def _build_config_panel(self) -> QGroupBox:
        group = QGroupBox("Experiment Settings")
        group.setFixedWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)

        self.trace_combo = QComboBox()
        self.trace_combo.addItems(TRACE_TYPES)
        form.addRow("Trace type", self.trace_combo)

        self.count_spin = QSpinBox()
        self.count_spin.setRange(0, 1_000_000)
        self.count_spin.setValue(32)
        form.addRow("Count", self.count_spin)

        self.cache_size_combo = QComboBox()
        self.cache_size_combo.addItems(["4096", "8192", "16384"])
        self.cache_size_combo.setCurrentText("8192")
        form.addRow("Cache size", self.cache_size_combo)

        self.block_size_combo = QComboBox()
        self.block_size_combo.addItems(["16", "32", "64"])
        self.block_size_combo.setCurrentText("32")
        form.addRow("Block size", self.block_size_combo)

        self.ways_combo = QComboBox()
        self.ways_combo.addItems(["1", "2", "4"])
        self.ways_combo.setCurrentText("2")
        form.addRow("Ways", self.ways_combo)

        self.policy_combo = QComboBox()
        self.policy_combo.addItems(["LRU", "FIFO", "Random"])
        form.addRow("Policy", self.policy_combo)
        layout.addLayout(form)

        self.run_button = QPushButton("Run Single Experiment")
        self.run_button.clicked.connect(self.run_single_experiment)
        layout.addWidget(self.run_button)

        self.export_button = QPushButton("Export Single Report")
        self.export_button.clicked.connect(self.export_current_report)
        layout.addWidget(self.export_button)

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        layout.addWidget(self.clear_button)
        layout.addStretch(1)
        return group

    def _build_results_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        stats_group = QGroupBox("Statistics")
        stats_form = QFormLayout(stats_group)
        self.total_label = QLabel("0")
        self.hits_label = QLabel("0")
        self.misses_label = QLabel("0")
        self.hit_rate_label = QLabel("0.00%")
        self.miss_rate_label = QLabel("0.00%")
        stats_form.addRow("Total accesses", self.total_label)
        stats_form.addRow("Hits", self.hits_label)
        stats_form.addRow("Misses", self.misses_label)
        stats_form.addRow("Hit rate", self.hit_rate_label)
        stats_form.addRow("Miss rate", self.miss_rate_label)
        layout.addWidget(stats_group, 0)

        log_group = QGroupBox("Access Log")
        log_layout = QVBoxLayout(log_group)
        self.access_table = QTableWidget(0, len(ACCESS_LOG_FIELDS))
        self.access_table.setHorizontalHeaderLabels(ACCESS_LOG_FIELDS)
        self._configure_table()
        self._configure_access_table_columns()
        log_layout.addWidget(self.access_table)
        layout.addWidget(log_group, 1)
        return panel

    def run_single_experiment(self) -> None:
        """Run one experiment from the current controls."""
        try:
            config = self._read_cache_config()
            trace_type = self.trace_combo.currentText()
            state = self.controller.run(
                f"{trace_type.title()} GUI Experiment",
                config,
                trace_type,
                {"count": self.count_spin.value()},
            )
        except Exception as exc:
            self._show_status(f"Experiment error: {exc}")
            QMessageBox.warning(self, "Experiment Error", str(exc))
            return

        self._render(state)
        summary = state.summary
        self._show_status(
            f"Trace: {trace_type} | Total: {summary['total_accesses']} | "
            f"Hit rate: {summary['hit_rate']:.2%} | "
            f"Miss rate: {summary['miss_rate']:.2%}"
        )

    def export_current_report(self) -> None:
        """Export CSV and Markdown files for the latest result."""
        if not self.controller.state.has_exportable_result:
            self._show_status("Export skipped: please run an experiment first.")
            QMessageBox.information(
                self,
                "Export Report",
                "Please run an experiment first.",
            )
            return

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            "outputs",
        )
        if not directory:
            return

        try:
            csv_path, report_path = self.controller.export(directory)
        except Exception as exc:
            self._show_status(f"Export error: {exc}")
            QMessageBox.warning(self, "Export Error", str(exc))
            return

        self._show_status(f"Export complete: {directory}")
        QMessageBox.information(
            self,
            "Export Complete",
            f"CSV exported:\n{csv_path}\n\nMarkdown report exported:\n{report_path}",
        )

    def clear_results(self) -> None:
        """Clear statistics, access rows, and retained result state."""
        state = self.controller.clear()
        self._render(state)
        self._show_status("Results cleared.")

    def _read_cache_config(self) -> CacheConfig:
        return CacheConfig(
            cache_size_bytes=int(self.cache_size_combo.currentText()),
            block_size_bytes=int(self.block_size_combo.currentText()),
            ways=int(self.ways_combo.currentText()),
            replacement_policy=self.policy_combo.currentText(),
        )

    def _render(self, state: SingleExperimentViewModel) -> None:
        summary = state.summary
        if summary is None:
            self.total_label.setText("0")
            self.hits_label.setText("0")
            self.misses_label.setText("0")
            self.hit_rate_label.setText("0.00%")
            self.miss_rate_label.setText("0.00%")
            self.access_table.setRowCount(0)
            return

        self.total_label.setText(str(summary["total_accesses"]))
        self.hits_label.setText(str(summary["hits"]))
        self.misses_label.setText(str(summary["misses"]))
        self.hit_rate_label.setText(f"{summary['hit_rate']:.2%}")
        self.miss_rate_label.setText(f"{summary['miss_rate']:.2%}")
        self._update_access_table(state.access_log)

    def _update_access_table(self, access_results) -> None:
        self.access_table.setRowCount(len(access_results))
        for row_index, result in enumerate(access_results):
            for col_index, field in enumerate(ACCESS_LOG_FIELDS):
                item = QTableWidgetItem(_format_cell(result.get(field), field))
                item.setTextAlignment(Qt.AlignCenter)
                self.access_table.setItem(row_index, col_index, item)
        self._configure_access_table_columns()

    def _configure_table(self) -> None:
        self.access_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.access_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.access_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.access_table.setAlternatingRowColors(True)

    def _configure_access_table_columns(self) -> None:
        header = self.access_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        column_widths = {
            "access_id": 78,
            "address": 96,
            "operation": 88,
            "tag": 72,
            "index": 72,
            "offset": 72,
            "hit": 72,
            "victim_way": 96,
            "replaced_valid": 116,
            "replaced_tag": 110,
        }
        for col_index, field in enumerate(ACCESS_LOG_FIELDS):
            self.access_table.setColumnWidth(
                col_index,
                column_widths.get(field, 90),
            )

    def _show_status(self, message: str) -> None:
        window = self.window()
        if hasattr(window, "statusBar"):
            window.statusBar().showMessage(message)


def _format_cell(value, field: str) -> str:
    if value is None:
        return ""
    if field == "hit":
        return "Hit" if value else "Miss"
    if field in {"hit_rate", "miss_rate"}:
        return f"{value:.2%}"
    return str(value)


__all__ = ["SingleExperimentWidget", "TRACE_TYPES"]
