"""PySide6 widget for the classic Compare Experiment lab."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from cachevis_rv.core import CacheConfig
from cachevis_rv.services import COMPARISON_FIELDS

from .controller import CompareExperimentController
from .view_model import CompareExperimentViewModel


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


class CompareExperimentWidget(QWidget):
    """Self-contained classic cache-parameter comparison page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = CompareExperimentController()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(12)
        layout.addWidget(self._build_config_panel(), 0)
        layout.addWidget(self._build_results_panel(), 1)

    def _build_config_panel(self) -> QGroupBox:
        group = QGroupBox("Compare Settings")
        group.setFixedWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)

        self.compare_trace_combo = QComboBox()
        self.compare_trace_combo.addItems(TRACE_TYPES)
        form.addRow("Trace type", self.compare_trace_combo)

        self.compare_count_spin = QSpinBox()
        self.compare_count_spin.setRange(0, 1_000_000)
        self.compare_count_spin.setValue(64)
        form.addRow("Count", self.compare_count_spin)

        self.compare_type_combo = QComboBox()
        self.compare_type_combo.addItems(["ways", "block-size", "cache-size"])
        form.addRow("Compare type", self.compare_type_combo)

        self.compare_policy_combo = QComboBox()
        self.compare_policy_combo.addItems(["LRU", "FIFO", "Random"])
        form.addRow("Policy", self.compare_policy_combo)
        layout.addLayout(form)

        self.run_compare_button = QPushButton("Run Compare Experiment")
        self.run_compare_button.clicked.connect(self.run_compare_experiment)
        layout.addWidget(self.run_compare_button)

        self.export_compare_button = QPushButton("Export Compare Report")
        self.export_compare_button.clicked.connect(self.export_compare_report)
        layout.addWidget(self.export_compare_button)

        self.clear_compare_button = QPushButton("Clear Compare Results")
        self.clear_compare_button.clicked.connect(self.clear_compare_results)
        layout.addWidget(self.clear_compare_button)
        layout.addStretch(1)
        return group

    def _build_results_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        group = QGroupBox("Comparison Results")
        group_layout = QVBoxLayout(group)
        self.compare_table = QTableWidget(0, len(COMPARISON_FIELDS))
        self.compare_table.setHorizontalHeaderLabels(COMPARISON_FIELDS)
        self._configure_table()
        self._configure_compare_table_columns()
        group_layout.addWidget(self.compare_table)
        layout.addWidget(group, 1)
        return panel

    def run_compare_experiment(self) -> None:
        """Run a comparison from the current controls."""
        trace_type = self.compare_trace_combo.currentText()
        compare_type = self.compare_type_combo.currentText()
        trace_params = {"count": self.compare_count_spin.value()}
        try:
            base_config = CacheConfig(
                cache_size_bytes=8192,
                block_size_bytes=32,
                ways=2,
                replacement_policy=self.compare_policy_combo.currentText(),
            )
            comparison_name = (
                f"{compare_type} GUI comparison on {trace_type} trace"
            )
            state = self.controller.run(
                comparison_name,
                compare_type,
                trace_type,
                trace_params,
                base_config,
            )
        except Exception as exc:
            self._show_status(f"Compare error: {exc}")
            QMessageBox.warning(self, "Compare Error", str(exc))
            return

        self._render(state)
        self._show_status(
            f"Compare: {compare_type} | Trace: {trace_type} | "
            f"Best hit rate: {state.best_hit_rate:.2%}"
        )

    def export_compare_report(self) -> None:
        """Export a Markdown report for the latest comparison."""
        if not self.controller.state.has_exportable_result:
            self._show_status(
                "Export skipped: please run a compare experiment first."
            )
            QMessageBox.information(
                self,
                "Export Compare Report",
                "Please run a compare experiment first.",
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
            report_path = self.controller.export(directory)
        except Exception as exc:
            self._show_status(f"Compare export error: {exc}")
            QMessageBox.warning(self, "Export Error", str(exc))
            return

        self._show_status(f"Compare report exported: {report_path}")
        QMessageBox.information(
            self,
            "Export Complete",
            f"Markdown comparison report exported:\n{report_path}",
        )

    def clear_compare_results(self) -> None:
        """Clear comparison rows and retained comparison state."""
        state = self.controller.clear()
        self._render(state)
        self._show_status("Compare results cleared.")

    def _render(self, state: CompareExperimentViewModel) -> None:
        self._update_compare_table(state.rows)

    def _update_compare_table(self, summaries) -> None:
        self.compare_table.setRowCount(len(summaries))
        for row_index, summary in enumerate(summaries):
            for col_index, field in enumerate(COMPARISON_FIELDS):
                item = QTableWidgetItem(_format_cell(summary.get(field), field))
                item.setTextAlignment(Qt.AlignCenter)
                self.compare_table.setItem(row_index, col_index, item)
        self._configure_compare_table_columns()

    def _configure_table(self) -> None:
        self.compare_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.compare_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.compare_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.compare_table.setAlternatingRowColors(True)

    def _configure_compare_table_columns(self) -> None:
        header = self.compare_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        column_widths = {
            "config_name": 120,
            "cache_size_bytes": 120,
            "block_size_bytes": 120,
            "ways": 70,
            "replacement_policy": 130,
            "total_accesses": 120,
            "hits": 80,
            "misses": 90,
            "hit_rate": 90,
            "miss_rate": 90,
        }
        for col_index, field in enumerate(COMPARISON_FIELDS):
            self.compare_table.setColumnWidth(
                col_index,
                column_widths.get(field, 100),
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


__all__ = ["CompareExperimentWidget", "TRACE_TYPES"]
