"""Formal total-cycle ranking and hit-rate/AMAT reversal display."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .sweep_table import display


class ComparisonPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceComparisonPanel")
        self.setStyleSheet(
            "QFrame#PerformanceComparisonPanel { background: #f5eefe; color: #43256a; border: 1px solid #aa8bce; border-radius: 8px; }"
            "QFrame#PerformanceComparisonPanel QLabel { color: #43256a; }"
        )
        layout = QVBoxLayout(self)
        self.title = QLabel("Hit Rate vs AMAT Tradeoff")
        self.title.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(self.title)
        self.summary = QLabel("Run a sweep to compare total cycles and AMAT.")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.pairs = QLabel("No hit-rate/AMAT ranking reversal in this sweep")
        self.pairs.setWordWrap(True)
        layout.addWidget(self.pairs)

    def render(self, model) -> None:
        if model is None:
            self.title.setText("Hit Rate vs AMAT Tradeoff")
            self.summary.setText("Run a sweep to compare total cycles and AMAT.")
            self.pairs.setText("No hit-rate/AMAT ranking reversal in this sweep")
            return
        self.title.setText(model.comparison_title)
        self.summary.setText(
            f"Fastest: {', '.join(model.fastest_point_labels) or 'N/A'} | "
            f"Slowest: {', '.join(model.slowest_point_labels) or 'N/A'} | "
            f"Speedup range: {display(model.minimum_speedup)} to {display(model.maximum_speedup)} | "
            f"All total cycles equal: {'Yes' if model.all_total_cycles_equal else 'No'}\n"
            + model.teaching_insight
        )
        if not model.tradeoff_pairs:
            self.pairs.setText("No hit-rate/AMAT ranking reversal in this sweep")
            return
        self.pairs.setText("\n\n".join(
            f"{pair.higher_hit_rate_label}: hit rate {pair.higher_hit_rate}, AMAT {pair.higher_amat}\n"
            f"{pair.lower_hit_rate_label}: hit rate {pair.lower_hit_rate}, AMAT {pair.lower_amat}\n{pair.explanation}"
            for pair in model.tradeoff_pairs
        ))


__all__ = ["ComparisonPanel"]
