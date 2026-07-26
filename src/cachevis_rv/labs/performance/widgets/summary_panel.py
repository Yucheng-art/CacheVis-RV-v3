"""Sweep summary with expected and observed facts kept separate."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class SummaryPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceSummaryPanel")
        self.setStyleSheet(
            "QFrame#PerformanceSummaryPanel { background: #eaf2ff; color: #17375e; border: 1px solid #8aa8cf; border-radius: 8px; }"
            "QFrame#PerformanceSummaryPanel QLabel { color: #17375e; }"
        )
        layout = QVBoxLayout(self)
        title = QLabel("Teaching Insight / Sweep Summary")
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(title)
        self.facts = QLabel("Run a sweep to compare explicit timing and cache behavior.")
        self.facts.setWordWrap(True)
        layout.addWidget(self.facts)
        self.expected = QLabel("Expected Teaching Conclusion: N/A")
        self.expected.setWordWrap(True)
        self.expected.setStyleSheet("background: #fff4d8; color: #5d4510; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.expected)
        self.actual = QLabel("Actual Observations: N/A")
        self.actual.setWordWrap(True)
        self.actual.setStyleSheet("background: #e5f7eb; color: #174d2d; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.actual)

    def render(self, model) -> None:
        if model is None:
            self.facts.setText("Run a sweep to compare explicit timing and cache behavior.")
            self.expected.setText("Expected Teaching Conclusion: N/A")
            self.actual.setText("Actual Observations: N/A")
            return
        self.facts.setText(
            f"{model.title} | Kind: {model.sweep_kind.value} | Baseline: {model.baseline_label} | Points: {model.point_count}\n"
            f"Best AMAT: {', '.join(model.best_amat_labels) or 'N/A'}{' (tie)' if model.best_amat_is_tie else ''}\n"
            f"Best Hit Rate: {', '.join(model.best_hit_rate_labels) or 'N/A'}{' (tie)' if model.best_hit_rate_is_tie else ''}\n"
            f"Lowest Traffic: {', '.join(model.lowest_traffic_labels) or 'N/A'}{' (tie)' if model.lowest_traffic_is_tie else ''}\n"
            f"Hit-rate and AMAT best agree: {'Yes' if model.hit_rate_and_amat_best_agree else 'No'}"
        )
        self.expected.setText("Expected Teaching Conclusion:\n" + model.expected_teaching_conclusion)
        self.actual.setText("Actual Observations:\n" + ("\n".join(f"• {item}" for item in model.actual_observations) or "N/A"))


__all__ = ["SummaryPanel"]
