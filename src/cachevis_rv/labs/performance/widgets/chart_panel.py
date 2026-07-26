"""Metric selection and lightweight chart rendering."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ..chart_view_model import PerformanceChartMetric
from .chart_canvas import PerformanceChartCanvas


class ChartPanel(QFrame):
    metric_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceChartPanel")
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        heading = QLabel("Metric Chart")
        heading.setStyleSheet("font-size: 18px; font-weight: 800;")
        top.addWidget(heading)
        top.addStretch(1)
        self.metric_combo = QComboBox()
        for metric in PerformanceChartMetric:
            self.metric_combo.addItem(metric.value.replace("_", " ").title(), metric.value)
        top.addWidget(self.metric_combo)
        layout.addLayout(top)
        self.canvas = PerformanceChartCanvas()
        layout.addWidget(self.canvas)
        self.metric_combo.currentIndexChanged.connect(self._emit_metric)

    def _emit_metric(self, _index: int) -> None:
        self.metric_selected.emit(
            PerformanceChartMetric(str(self.metric_combo.currentData()))
        )

    def render(self, series, metric=None) -> None:
        if metric is not None:
            index = self.metric_combo.findData(metric.value)
            if index >= 0 and index != self.metric_combo.currentIndex():
                self.metric_combo.blockSignals(True)
                self.metric_combo.setCurrentIndex(index)
                self.metric_combo.blockSignals(False)
        self.canvas.render(series)


__all__ = ["ChartPanel"]
