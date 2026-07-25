"""PySide6 main window for CacheVis-RV."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from cache_config import CacheConfig
from compare_runner import build_comparison_configs, run_comparison
from experiment_runner import (
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    make_single_experiment_conclusion,
    run_single_experiment,
)
from report_exporter import (
    ACCESS_LOG_FIELDS,
    COMPARISON_FIELDS,
    export_access_log_csv,
    export_comparison_markdown_report,
    export_markdown_report,
)
from visualizer_widget import AddressVisualizerWidget
from version import APP_DESCRIPTION


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

ABOUT_TITLE = "About CacheVis-RV"
ABOUT_TEXT = (
    f"{SOFTWARE_NAME}\n"
    f"Version: {SOFTWARE_VERSION}\n\n"
    f"{APP_DESCRIPTION}\n\n"
    "Current support:\n"
    "- Single experiment GUI\n"
    "- GUI parameter comparison experiments\n"
    "- CLI experiments\n"
    "- CSV/Markdown export\n\n"
    "Not yet supported:\n"
    "- EXE packaging\n"
    "- Formal copyright application material generation"
)


class CacheVisMainWindow(QMainWindow):
    """Main desktop window for cache experiments."""

    def __init__(self) -> None:
        super().__init__()
        self.current_config = None
        self.current_summary = None
        self.current_compare_summaries = []
        self.current_compare_context = None
        self.setWindowTitle(f"{SOFTWARE_NAME} {SOFTWARE_VERSION}")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 680)
        self._build_ui()
        self._build_menu()
        self.statusBar().showMessage("Ready. Choose a tab and run an experiment.")

    def _build_ui(self) -> None:
        tabs = QTabWidget()
        tabs.addTab(AddressVisualizerWidget(), "Address Visualizer")
        tabs.addTab(self._build_single_tab(), "Single Experiment")
        tabs.addTab(self._build_compare_tab(), "Compare Experiment")
        self.setCentralWidget(tabs)

    def _build_menu(self) -> None:
        help_menu = self.menuBar().addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _build_single_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(12)
        layout.addWidget(self._build_single_config_panel(), 0)
        layout.addWidget(self._build_single_results_panel(), 1)
        return page

    def _build_single_config_panel(self) -> QGroupBox:
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

    def _build_single_results_panel(self) -> QWidget:
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
        self._configure_table(self.access_table)
        self._configure_access_table_columns()
        log_layout.addWidget(self.access_table)
        layout.addWidget(log_group, 1)

        return panel

    def _build_compare_tab(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(12)
        layout.addWidget(self._build_compare_config_panel(), 0)
        layout.addWidget(self._build_compare_results_panel(), 1)
        return page

    def _build_compare_config_panel(self) -> QGroupBox:
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

    def _build_compare_results_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        group = QGroupBox("Comparison Results")
        group_layout = QVBoxLayout(group)
        self.compare_table = QTableWidget(0, len(COMPARISON_FIELDS))
        self.compare_table.setHorizontalHeaderLabels(COMPARISON_FIELDS)
        self._configure_table(self.compare_table)
        self._configure_compare_table_columns()
        group_layout.addWidget(self.compare_table)
        layout.addWidget(group, 1)
        return panel

    def _configure_table(self, table: QTableWidget) -> None:
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)

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
            self.access_table.setColumnWidth(col_index, column_widths.get(field, 90))

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
            self.compare_table.setColumnWidth(col_index, column_widths.get(field, 100))

    def run_single_experiment(self) -> None:
        """Run one experiment from current UI settings and update the window."""
        try:
            config = self._read_cache_config()
            trace_type = self.trace_combo.currentText()
            summary = run_single_experiment(
                f"{trace_type.title()} GUI Experiment",
                config,
                trace_type,
                {"count": self.count_spin.value()},
                export=False,
            )
        except Exception as exc:
            self.statusBar().showMessage(f"Experiment error: {exc}")
            QMessageBox.warning(self, "Experiment Error", str(exc))
            return

        self.current_config = config
        self.current_summary = summary
        self._update_statistics(summary)
        self._update_access_table(summary["access_results"])
        self.statusBar().showMessage(
            f"Trace: {trace_type} | Total: {summary['total_accesses']} | "
            f"Hit rate: {summary['hit_rate']:.2%} | Miss rate: {summary['miss_rate']:.2%}"
        )

    def run_compare_experiment(self) -> None:
        """Run a cache parameter comparison and update the comparison table."""
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
            configs = build_comparison_configs(compare_type, base_config)
            comparison_name = f"{compare_type} GUI comparison on {trace_type} trace"
            summaries = run_comparison(
                comparison_name,
                trace_type,
                trace_params,
                configs,
                export=False,
            )
        except Exception as exc:
            self.statusBar().showMessage(f"Compare error: {exc}")
            QMessageBox.warning(self, "Compare Error", str(exc))
            return

        self.current_compare_summaries = summaries
        self.current_compare_context = {
            "comparison_name": comparison_name,
            "trace_type": trace_type,
            "trace_params": trace_params,
            "compare_type": compare_type,
        }
        self._update_compare_table(summaries)
        best_hit_rate = max((row["hit_rate"] for row in summaries), default=0.0)
        self.statusBar().showMessage(
            f"Compare: {compare_type} | Trace: {trace_type} | "
            f"Best hit rate: {best_hit_rate:.2%}"
        )

    def export_current_report(self) -> None:
        """Export CSV and Markdown files for the latest single experiment."""
        if not self.current_summary or not self.current_config:
            self.statusBar().showMessage("Export skipped: please run an experiment first.")
            QMessageBox.information(self, "Export Report", "Please run an experiment first.")
            return

        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory", "outputs")
        if not directory:
            return

        try:
            export_dir = Path(directory)
            safe_name = _safe_file_name(self.current_summary["experiment_name"])
            csv_path = export_dir / f"{safe_name}_access_log.csv"
            report_path = export_dir / f"{safe_name}_report.md"
            export_access_log_csv(self.current_summary["access_results"], csv_path)
            export_markdown_report(
                report_path,
                software_name=SOFTWARE_NAME,
                software_version=SOFTWARE_VERSION,
                experiment_name=self.current_summary["experiment_name"],
                cache_config=self.current_config,
                trace_type=self.current_summary["trace_type"],
                summary=self.current_summary,
                conclusion=make_single_experiment_conclusion(self.current_summary),
            )
        except Exception as exc:
            self.statusBar().showMessage(f"Export error: {exc}")
            QMessageBox.warning(self, "Export Error", str(exc))
            return

        self.statusBar().showMessage(f"Export complete: {export_dir}")
        QMessageBox.information(
            self,
            "Export Complete",
            f"CSV exported:\n{csv_path}\n\nMarkdown report exported:\n{report_path}",
        )

    def export_compare_report(self) -> None:
        """Export a Markdown report for the latest comparison experiment."""
        if not self.current_compare_summaries or not self.current_compare_context:
            self.statusBar().showMessage("Export skipped: please run a compare experiment first.")
            QMessageBox.information(
                self,
                "Export Compare Report",
                "Please run a compare experiment first.",
            )
            return

        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory", "outputs")
        if not directory:
            return

        try:
            export_dir = Path(directory)
            report_path = export_dir / (
                f"{_safe_file_name(self.current_compare_context['comparison_name'])}.md"
            )
            export_comparison_markdown_report(
                report_path,
                software_name=SOFTWARE_NAME,
                software_version=SOFTWARE_VERSION,
                comparison_name=self.current_compare_context["comparison_name"],
                trace_type=self.current_compare_context["trace_type"],
                trace_params=self.current_compare_context["trace_params"],
                summaries=self.current_compare_summaries,
            )
        except Exception as exc:
            self.statusBar().showMessage(f"Compare export error: {exc}")
            QMessageBox.warning(self, "Export Error", str(exc))
            return

        self.statusBar().showMessage(f"Compare report exported: {report_path}")
        QMessageBox.information(
            self,
            "Export Complete",
            f"Markdown comparison report exported:\n{report_path}",
        )

    def clear_results(self) -> None:
        """Clear single experiment statistics, access table, and cached data."""
        self.current_config = None
        self.current_summary = None
        self.total_label.setText("0")
        self.hits_label.setText("0")
        self.misses_label.setText("0")
        self.hit_rate_label.setText("0.00%")
        self.miss_rate_label.setText("0.00%")
        self.access_table.setRowCount(0)
        self.statusBar().showMessage("Results cleared.")

    def clear_compare_results(self) -> None:
        """Clear comparison table and cached comparison data."""
        self.current_compare_summaries = []
        self.current_compare_context = None
        self.compare_table.setRowCount(0)
        self.statusBar().showMessage("Compare results cleared.")

    def show_about_dialog(self) -> None:
        """Show basic software information."""
        create_about_message_box(self).exec()

    def _read_cache_config(self) -> CacheConfig:
        return CacheConfig(
            cache_size_bytes=int(self.cache_size_combo.currentText()),
            block_size_bytes=int(self.block_size_combo.currentText()),
            ways=int(self.ways_combo.currentText()),
            replacement_policy=self.policy_combo.currentText(),
        )

    def _update_statistics(self, summary: dict) -> None:
        self.total_label.setText(str(summary["total_accesses"]))
        self.hits_label.setText(str(summary["hits"]))
        self.misses_label.setText(str(summary["misses"]))
        self.hit_rate_label.setText(f"{summary['hit_rate']:.2%}")
        self.miss_rate_label.setText(f"{summary['miss_rate']:.2%}")

    def _update_access_table(self, access_results: list[dict]) -> None:
        self.access_table.setRowCount(len(access_results))
        for row_index, result in enumerate(access_results):
            for col_index, field in enumerate(ACCESS_LOG_FIELDS):
                item = QTableWidgetItem(_format_cell(result.get(field), field))
                item.setTextAlignment(Qt.AlignCenter)
                self.access_table.setItem(row_index, col_index, item)
        self._configure_access_table_columns()

    def _update_compare_table(self, summaries: list[dict]) -> None:
        self.compare_table.setRowCount(len(summaries))
        for row_index, summary in enumerate(summaries):
            for col_index, field in enumerate(COMPARISON_FIELDS):
                item = QTableWidgetItem(_format_cell(summary.get(field), field))
                item.setTextAlignment(Qt.AlignCenter)
                self.compare_table.setItem(row_index, col_index, item)
        self._configure_compare_table_columns()


def _format_cell(value, field: str) -> str:
    if value is None:
        return ""
    if field == "hit":
        return "Hit" if value else "Miss"
    if field in {"hit_rate", "miss_rate"}:
        return f"{value:.2%}"
    return str(value)


def _safe_file_name(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")


def create_about_message_box(parent: QWidget | None = None) -> QMessageBox:
    """Create the About dialog so tools can capture the same GUI content."""
    box = QMessageBox(parent)
    box.setWindowTitle(ABOUT_TITLE)
    box.setText(ABOUT_TEXT)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return box
