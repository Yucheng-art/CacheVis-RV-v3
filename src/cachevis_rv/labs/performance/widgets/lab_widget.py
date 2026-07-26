"""Scrollable Performance Lab GUI orchestrated exclusively by its controller."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..controller import PerformanceController
from ..page_state import PerformancePageState
from .chart_panel import ChartPanel
from .comparison_panel import ComparisonPanel
from .experiment_controls import ExperimentControls
from .hierarchy_panel import HierarchyPanel
from .selected_point_panel import SelectedPointPanel
from .summary_panel import SummaryPanel
from .sweep_table import SweepTable


class PerformanceLabWidget(QScrollArea):
    """Complete M4.3 page; child widgets only render published models."""

    def __init__(self, parent=None, controller=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceLabWidget")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.controller = controller if controller is not None else PerformanceController()
        self._build_ui()
        self._connect_signals()
        self._render(self.controller.state)

    def _build_ui(self) -> None:
        content = QWidget()
        content.setObjectName("PerformanceLabContent")
        content.setStyleSheet(
            "QWidget#PerformanceLabContent { background: #0b1220; color: #eef4ff; }"
            "QWidget#PerformanceLabContent QLabel { color: #eef4ff; }"
            "QWidget#PerformanceLabContent QFrame { border-radius: 7px; }"
        )
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 32)
        layout.setSpacing(16)
        title = QLabel("Performance Lab")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        subtitle = QLabel("Model cache performance under explicit timing assumptions — hit rate is evidence, not the complete performance answer.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #b6c5da;")
        layout.addWidget(subtitle)
        flow = QLabel("Cache Configuration + Timing Assumptions + Trace  →  Hits / Misses  →  Lookup + Miss Stall Cycles  →  Total Cycles / AMAT / Traffic  →  Sweep Comparison  →  Performance Tradeoff")
        flow.setWordWrap(True)
        flow.setStyleSheet("background: #dcecff; color: #163a63; padding: 10px; border: 1px solid #7ea7d2; border-radius: 7px; font-weight: 700;")
        layout.addWidget(flow)

        self.controls = ExperimentControls()
        layout.addWidget(self.controls)
        self.summary_panel = SummaryPanel()
        layout.addWidget(self.summary_panel)
        self.chart_panel = ChartPanel()
        layout.addWidget(self.chart_panel)
        table_heading = QLabel("Sweep Point Comparison Table")
        table_heading.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(table_heading)
        self.sweep_table = SweepTable()
        layout.addWidget(self.sweep_table)
        self.selected_point_panel = SelectedPointPanel()
        layout.addWidget(self.selected_point_panel)
        self.comparison_panel = ComparisonPanel()
        layout.addWidget(self.comparison_panel)
        self.hierarchy_panel = HierarchyPanel()
        layout.addWidget(self.hierarchy_panel)
        layout.addStretch(1)
        self.setWidget(content)

    def _connect_signals(self) -> None:
        self.controls.run_requested.connect(self.run_sweep)
        self.controls.clear_requested.connect(self.clear_sweep)
        self.chart_panel.metric_selected.connect(self.select_chart_metric)
        self.sweep_table.point_selected.connect(self.select_point)
        self.hierarchy_panel.analyze_requested.connect(self.analyze_hierarchy)
        self.hierarchy_panel.clear_requested.connect(self.clear_hierarchy)

    def run_sweep(self) -> bool:
        try:
            state = self.controller.run_sweep(self.controls.build_definition())
        except (TypeError, ValueError) as exc:
            self._show_error("Invalid Performance sweep", str(exc))
            return False
        self._render(state)
        return True

    def clear_sweep(self) -> None:
        self._render(self.controller.clear_sweep())

    def select_point(self, point_id: str) -> bool:
        try:
            state = self.controller.select_point(point_id)
        except (RuntimeError, ValueError) as exc:
            self._show_error("Point selection failed", str(exc))
            return False
        self._render(state)
        return True

    def select_chart_metric(self, metric) -> bool:
        if not self.controller.state.has_sweep_result:
            return False
        try:
            state = self.controller.select_chart_metric(metric)
        except (RuntimeError, ValueError) as exc:
            self._show_error("Metric selection failed", str(exc))
            return False
        self._render(state)
        return True

    def analyze_hierarchy(self, model=None) -> bool:
        try:
            state = self.controller.analyze_hierarchy(
                model if model is not None else self.hierarchy_panel.build_model()
            )
        except (TypeError, ValueError) as exc:
            self._show_error("Invalid hierarchy model", str(exc))
            return False
        self._render(state)
        return True

    def clear_hierarchy(self) -> None:
        self._render(self.controller.clear_hierarchy())

    def clear_all(self) -> None:
        self._render(self.controller.clear_all())

    def _render(self, state: PerformancePageState) -> None:
        self.summary_panel.render(state.sweep_summary)
        self.chart_panel.render(state.chart_series, state.chart_metric)
        self.sweep_table.render(state.point_view_models)
        self.selected_point_panel.render(state.selected_point)
        self.comparison_panel.render(state.comparison_view)
        self.hierarchy_panel.render(state.hierarchy_view)

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.warning(self, title, message)


__all__ = ["PerformanceLabWidget"]
