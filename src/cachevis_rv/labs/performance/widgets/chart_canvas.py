"""Dependency-free QPainter chart for formal chart series values."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget


class PerformanceChartCanvas(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceChartCanvas")
        self.setMinimumHeight(270)
        self.setMinimumWidth(440)
        self._series = None

    def render(self, series) -> None:
        self._series = series
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f8fbff"))
        painter.setPen(QColor("#19324d"))
        if self._series is None:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Run a sweep to draw a metric")
            return
        painter.setFont(QFont(painter.font().family(), 11, QFont.Weight.Bold))
        painter.drawText(QRectF(12, 8, self.width() - 24, 26), Qt.AlignmentFlag.AlignCenter, self._series.title)
        points = self._series.points
        available = [(index, point) for index, point in enumerate(points) if point.y_value is not None]
        if not available:
            painter.drawText(QRectF(20, 45, self.width() - 40, 150), Qt.AlignmentFlag.AlignCenter, "No data — values are N/A")
            self._draw_labels(painter, points)
            return
        chart = QRectF(65, 48, max(120, self.width() - 95), max(100, self.height() - 110))
        painter.setPen(QPen(QColor("#526b85"), 1))
        painter.drawLine(chart.bottomLeft(), chart.bottomRight())
        painter.drawLine(chart.bottomLeft(), chart.topLeft())
        values = [float(point.y_value) for _, point in available]
        low, high = min(values), max(values)
        span = high - low
        if span == 0:
            span = 1.0
            low -= 0.5
        coordinates = {}
        for index, point in available:
            x = chart.left() + (chart.width() / 2 if len(points) == 1 else chart.width() * index / max(1, len(points) - 1))
            y = chart.bottom() - chart.height() * (float(point.y_value) - low) / span
            coordinates[index] = QPointF(x, y)
        painter.setPen(QPen(QColor("#6282a4"), 2))
        ordered = [coordinates[index] for index, _point in available]
        for first, second in zip(ordered, ordered[1:]):
            painter.drawLine(first, second)
        for index, point in enumerate(points):
            if index not in coordinates:
                continue
            center = coordinates[index]
            color = QColor("#16794a") if point.is_best_for_metric else QColor("#3978c6")
            painter.setBrush(color)
            painter.setPen(QPen(QColor("#102a43"), 2 if point.is_selected else 1))
            radius = 8 if point.is_selected else 6
            painter.drawEllipse(center, radius, radius)
            if point.is_baseline:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(QColor("#d17a00"), 2))
                painter.drawEllipse(center, radius + 4, radius + 4)
        self._draw_labels(painter, points, chart)

    def _draw_labels(self, painter, points, chart=None) -> None:
        painter.setFont(QFont(painter.font().family(), 8))
        width = max(1, self.width() - 80)
        for index, point in enumerate(points):
            x = 45 + (width / 2 if len(points) == 1 else width * index / max(1, len(points) - 1))
            marker = "B " if point.is_baseline else ""
            marker += "S " if point.is_selected else ""
            marker += "★ " if point.is_best_for_metric else ""
            painter.setPen(QColor("#19324d"))
            painter.drawText(QRectF(x - 55, self.height() - 55, 110, 42), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, f"{marker}{point.label}\nx={point.x_value}, y={'N/A' if point.y_value is None else point.y_value}")
        if chart is not None:
            painter.save()
            painter.translate(14, chart.center().y())
            painter.rotate(-90)
            painter.drawText(QRectF(-90, -10, 180, 20), Qt.AlignmentFlag.AlignCenter, self._series.y_axis_label)
            painter.restore()
            painter.drawText(QRectF(chart.left(), self.height() - 18, chart.width(), 16), Qt.AlignmentFlag.AlignCenter, self._series.x_axis_label)


__all__ = ["PerformanceChartCanvas"]
