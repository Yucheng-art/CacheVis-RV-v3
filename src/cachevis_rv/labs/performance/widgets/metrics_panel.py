"""Selected-point formal metric and invariant display."""

from PySide6.QtWidgets import QFormLayout, QFrame, QLabel, QVBoxLayout

from .sweep_table import display


class MetricsPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceMetricsPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Performance Metrics & Invariants")
        heading.setStyleSheet("font-size: 16px; font-weight: 750;")
        layout.addWidget(heading)
        form = QFormLayout()
        names = (
            "Accesses", "Hits / Misses", "Hit / Miss Rate", "Lookup Cycles",
            "Miss Stall Cycles", "Total Cycles", "AMAT", "Line Fills",
            "Bytes Fetched", "Bytes / Access", "Miss Stall Fraction",
            "Hits + Misses = Accesses", "Cycle Decomposition", "AMAT Invariant", "Traffic Relation",
        )
        self.labels = {}
        for name in names:
            label = QLabel("N/A")
            label.setTextInteractionFlags(label.textInteractionFlags())
            self.labels[name] = label
            form.addRow(name, label)
        layout.addLayout(form)

    def render(self, metrics) -> None:
        if metrics is None:
            for label in self.labels.values():
                label.setText("N/A")
            return
        values = {
            "Accesses": metrics.accesses,
            "Hits / Misses": f"{metrics.hits} / {metrics.misses}",
            "Hit / Miss Rate": f"{metrics.hit_rate} / {metrics.miss_rate}",
            "Lookup Cycles": metrics.total_lookup_cycles,
            "Miss Stall Cycles": metrics.total_miss_penalty_cycles,
            "Total Cycles": metrics.total_cycles,
            "AMAT": metrics.amat_display,
            "Line Fills": metrics.line_fills,
            "Bytes Fetched": metrics.bytes_fetched,
            "Bytes / Access": metrics.bytes_per_access_display,
            "Miss Stall Fraction": metrics.miss_stall_fraction_display,
            "Hits + Misses = Accesses": _ok(metrics.access_invariant_ok),
            "Cycle Decomposition": _ok(metrics.cycle_decomposition_ok),
            "AMAT Invariant": _ok(metrics.amat_invariant_ok),
            "Traffic Relation": _ok(metrics.traffic_invariant_ok),
        }
        for name, value in values.items():
            self.labels[name].setText(display(value))


def _ok(value: bool) -> str:
    return "OK" if value else "CHECK"


__all__ = ["MetricsPanel"]
