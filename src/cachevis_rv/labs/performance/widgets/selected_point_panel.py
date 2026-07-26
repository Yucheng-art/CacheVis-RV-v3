"""Selected point configuration, timing, deltas, and metrics."""

from PySide6.QtWidgets import QFormLayout, QFrame, QGridLayout, QLabel, QVBoxLayout

from .metrics_panel import MetricsPanel
from .sweep_table import display


class SelectedPointPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceSelectedPointPanel")
        layout = QVBoxLayout(self)
        self.heading = QLabel("Selected Point Detail")
        self.heading.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(self.heading)
        grid = QGridLayout()
        self.config_labels = self._section(grid, 0, "Configuration", ("Cache Size", "Block Size", "Ways", "Sets", "Policy", "Address Width"))
        self.timing_labels = self._section(grid, 1, "Timing", ("Hit Time", "Fixed Overhead", "Transfer / Byte", "Effective Penalty"))
        self.delta_labels = self._section(grid, 2, "Baseline Comparison", ("AMAT Delta", "Cycle Delta", "Speedup"))
        layout.addLayout(grid)
        self.metrics_panel = MetricsPanel()
        layout.addWidget(self.metrics_panel)

    @staticmethod
    def _section(grid, column, title, fields):
        frame = QFrame()
        box = QVBoxLayout(frame)
        heading = QLabel(title)
        heading.setStyleSheet("font-weight: 750;")
        box.addWidget(heading)
        form = QFormLayout()
        labels = {}
        for field in fields:
            labels[field] = QLabel("N/A")
            form.addRow(field, labels[field])
        box.addLayout(form)
        grid.addWidget(frame, 0, column)
        return labels

    def render(self, point) -> None:
        if point is None:
            self.heading.setText("Selected Point Detail")
            for labels in (self.config_labels, self.timing_labels, self.delta_labels):
                for label in labels.values():
                    label.setText("N/A")
            self.metrics_panel.render(None)
            return
        self.heading.setText(f"Selected Point Detail — {point.label}")
        config = point.config
        timing = point.timing
        config_values = (config.cache_size_bytes, config.block_size_bytes, config.ways, config.sets, config.replacement_policy, config.address_bits)
        for label, value in zip(self.config_labels.values(), config_values):
            label.setText(display(value))
        timing_values = (timing.hit_time_cycles, timing.fixed_miss_overhead_cycles, timing.transfer_cycles_per_byte, point.metrics.effective_miss_penalty_cycles)
        for label, value in zip(self.timing_labels.values(), timing_values):
            label.setText(display(value))
        delta_values = (point.amat_delta_vs_baseline, point.total_cycles_delta_vs_baseline, point.speedup_vs_baseline)
        for label, value in zip(self.delta_labels.values(), delta_values):
            label.setText(display(value))
        self.metrics_panel.render(point.metrics)


__all__ = ["SelectedPointPanel"]
