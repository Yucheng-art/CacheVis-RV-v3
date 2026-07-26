"""Observed victim/state/outcome divergence summary."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ..divergence_view_model import PolicyDivergenceSummaryViewModel


class DivergencePanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyDivergencePanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Divergence Summary / Latest Execution")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.title_label = QLabel("No divergence observed")
        self.title_label.setObjectName("PolicyDivergenceTitle")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 800;")
        layout.addWidget(self.title_label)
        self.chain_label = QLabel("Victim → State → Outcome")
        self.chain_label.setStyleSheet(
            "background: #e8eef6; color: #20364d; border: 1px solid #8ba2ba;"
            "border-radius: 6px; padding: 7px; font-weight: 750;"
        )
        layout.addWidget(self.chain_label)
        grid = QGridLayout()
        self.values: dict[str, QLabel] = {}
        fields = (
            ("first_victim", "First Victim Divergence"),
            ("first_state", "First State Divergence"),
            ("first_outcome", "First Outcome Divergence"),
            ("lag", "Divergence Lag"),
            ("latest_victim", "Latest Victim Diverged?"),
            ("latest_state", "Latest State Diverged?"),
            ("latest_outcome", "Latest Outcome Diverged?"),
        )
        for index, (key, caption) in enumerate(fields):
            grid.addWidget(QLabel(caption), index // 4 * 2, index % 4)
            value = QLabel("N/A")
            value.setObjectName(f"PolicyDivergence_{key}")
            value.setStyleSheet("font-weight: 750;")
            grid.addWidget(value, index // 4 * 2 + 1, index % 4)
            self.values[key] = value
        layout.addLayout(grid)
        self.insight_label = QLabel()
        self.insight_label.setWordWrap(True)
        layout.addWidget(self.insight_label)

    def render(self, model: PolicyDivergenceSummaryViewModel) -> None:
        self.title_label.setText(model.summary_title)
        self.values["first_victim"].setText(self._step(model.first_victim_divergence_step))
        self.values["first_state"].setText(self._step(model.first_state_divergence_step))
        self.values["first_outcome"].setText(self._step(model.first_outcome_divergence_step))
        self.values["lag"].setText(
            "N/A" if model.divergence_lag_steps is None
            else f"{model.divergence_lag_steps} step(s)"
        )
        self.values["latest_victim"].setText(self._yes_no(model.latest_victim_diverged))
        self.values["latest_state"].setText(self._yes_no(model.latest_state_diverged))
        self.values["latest_outcome"].setText(self._yes_no(model.latest_outcome_diverged))
        self.insight_label.setText(model.teaching_insight)
        if model.has_any_outcome_divergence:
            colors = ("#ffe1e1", "#b85c5c", "#6f1d1d")
        elif model.has_any_state_divergence or model.has_any_victim_divergence:
            colors = ("#ffebcc", "#cf923d", "#6f3b00")
        else:
            colors = ("#e5edf5", "#8ba2ba", "#20364d")
        background, border, text = colors
        self.setStyleSheet(
            "QFrame#PolicyDivergencePanel {"
            f"background: {background}; border: 1px solid {border};"
            "border-radius: 8px; }"
            f"QFrame#PolicyDivergencePanel QLabel {{ color: {text}; }}"
        )

    @staticmethod
    def _step(value: int | None) -> str:
        return "Not yet" if value is None else f"Step {value + 1}"

    @staticmethod
    def _yes_no(value: bool) -> str:
        return "Yes" if value else "No"


__all__ = ["DivergencePanel"]
