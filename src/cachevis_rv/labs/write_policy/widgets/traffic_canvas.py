from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class TrafficCanvas(QWidget):
    """Lightweight runtime/final-drain bar comparison; exact values stay in tables."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._models = ()
        self.setMinimumHeight(190)

    def render(self, models):
        self._models = tuple(models)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0d1727"))
        painter.setPen(QColor("#dce8f7"))
        painter.drawText(12, 20, "Runtime       Including Final Dirty Drain")
        if not self._models:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No experiment loaded")
            return
        maximum = max((model.total_lower_memory_bytes_with_final_drain for model in self._models), default=0)
        maximum = max(maximum, 1)
        usable = max(self.width() - 160, 40)
        for row, model in enumerate(self._models):
            y = 38 + row * 34
            painter.setPen(QColor("#dce8f7")); painter.drawText(10, y + 16, model.lane_label)
            runtime_width = usable * model.total_lower_memory_bytes / maximum
            drain_width = usable * model.total_lower_memory_bytes_with_final_drain / maximum
            painter.fillRect(QRectF(105, y, runtime_width, 11), QColor("#55a9e8"))
            painter.fillRect(QRectF(105, y + 14, drain_width, 11), QColor("#e8b04f"))
            painter.setPen(QColor("#dce8f7")); painter.drawText(110 + usable, y + 18, f"{model.total_lower_memory_bytes} / {model.total_lower_memory_bytes_with_final_drain} B")


__all__ = ["TrafficCanvas"]
