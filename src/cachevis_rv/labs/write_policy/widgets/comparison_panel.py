from PySide6.QtWidgets import QLabel, QGridLayout, QVBoxLayout, QWidget

from .common import section_frame, value_text


class ComparisonPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Policy Comparison Summary")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        self.grid = QGridLayout(); layout.addLayout(self.grid)
        self.labels = {}
        names = ("Runtime Lowest Traffic", "Lowest Including Drain", "Highest Hit Rate",
                 "Runtime/Drain Leaders Agree", "Allocation Changed Future Outcome",
                 "Propagation Changed Dirty State", "Propagation Changed Runtime Traffic",
                 "Dirty Eviction Observed", "Bypass Observed")
        for row, name in enumerate(names):
            self.grid.addWidget(QLabel(name), row, 0)
            label = QLabel("N/A"); label.setWordWrap(True); self.grid.addWidget(label, row, 1); self.labels[name] = label
        self.observations = QLabel("N/A"); self.observations.setWordWrap(True); layout.addWidget(self.observations)
        self.caution = QLabel("N/A"); self.caution.setWordWrap(True); self.caution.setStyleSheet("color: #ffd98a;"); layout.addWidget(self.caution)

    def render(self, model):
        if model is None:
            for label in self.labels.values(): label.setText("N/A")
            self.observations.setText("N/A"); self.caution.setText("N/A"); return
        data = {
            "Runtime Lowest Traffic": f"{', '.join(model.runtime_lowest_traffic_lane_labels)} | Tie: {value_text(model.runtime_lowest_traffic_is_tie)}",
            "Lowest Including Drain": f"{', '.join(model.with_drain_lowest_traffic_lane_labels)} | Tie: {value_text(model.with_drain_lowest_traffic_is_tie)}",
            "Highest Hit Rate": f"{', '.join(model.highest_hit_rate_lane_labels)} | Tie: {value_text(model.highest_hit_rate_is_tie)}",
            "Runtime/Drain Leaders Agree": value_text(model.runtime_and_drain_leaders_agree),
            "Allocation Changed Future Outcome": value_text(model.allocation_changed_future_outcome),
            "Propagation Changed Dirty State": value_text(model.propagation_changed_dirty_state),
            "Propagation Changed Runtime Traffic": value_text(model.propagation_changed_runtime_traffic),
            "Dirty Eviction Observed": value_text(model.dirty_eviction_observed),
            "Bypass Observed": value_text(model.bypass_observed),
        }
        for name, value in data.items(): self.labels[name].setText(value)
        self.observations.setText("Actual Observations\n" + "\n".join(f"• {item}" for item in model.actual_observations))
        self.caution.setText(model.caution_note)


__all__ = ["ComparisonPanel"]
