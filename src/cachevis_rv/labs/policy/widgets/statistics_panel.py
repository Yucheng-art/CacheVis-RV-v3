"""Authoritative three-policy statistics comparison."""

from PySide6.QtWidgets import QFrame, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from ..statistics_view_model import PolicyComparisonStatisticsViewModel


class StatisticsPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyStatisticsPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Statistics Comparison / Latest Execution")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.table = QTableWidget(7, 4)
        self.table.setObjectName("PolicyStatisticsTable")
        self.table.setHorizontalHeaderLabels(("Metric", "LRU", "FIFO", "Random"))
        self.table.setVerticalHeaderLabels(["" for _ in range(7)])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(245)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.comparison_label = QLabel()
        self.comparison_label.setWordWrap(True)
        layout.addWidget(self.comparison_label)
        self.invariant_label = QLabel()
        self.invariant_label.setWordWrap(True)
        layout.addWidget(self.invariant_label)

    def render(self, model: PolicyComparisonStatisticsViewModel) -> None:
        rows = (
            ("Accesses", "accesses"),
            ("Hits", "hits"),
            ("Misses", "misses"),
            ("Invalid Fills", "invalid_fills"),
            ("Evictions", "evictions"),
            ("Hit Rate", "hit_rate"),
            ("Miss Rate", "miss_rate"),
        )
        lanes = {lane.policy: lane for lane in model.lane_statistics}
        for row, (caption, attribute) in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(caption))
            for column, policy in enumerate(("LRU", "FIFO", "Random"), start=1):
                lane = lanes.get(policy)
                value = getattr(lane, attribute) if lane is not None else 0
                text = f"{value:.1%}" if attribute.endswith("rate") else str(value)
                self.table.setItem(row, column, QTableWidgetItem(text))
        self.comparison_label.setText(
            f"All-agree steps: {model.all_agree_steps}   ·   "
            f"Outcome divergence: {model.outcome_divergence_steps}   ·   "
            f"Victim divergence: {model.victim_divergence_steps}   ·   "
            f"State divergence: {model.state_divergence_steps}\n"
            + self._leader_text(model)
        )
        lane_checks = all(
            lane.access_invariant_ok and lane.miss_partition_invariant_ok
            for lane in model.lane_statistics
        )
        self.invariant_label.setText(
            f"{'✓' if lane_checks else '⚠'} Hits + Misses = Accesses; "
            f"Invalid Fills + Evictions = Misses   ·   "
            f"{'✓' if model.outcome_partition_invariant_ok else '⚠'} "
            "All Agree + Outcome Divergence = Accesses"
        )

    @staticmethod
    def _leader_text(model: PolicyComparisonStatisticsViewModel) -> str:
        if not model.lane_statistics:
            return "Current trace: no accesses yet."
        maximum = max(lane.hits for lane in model.lane_statistics)
        leaders = [lane.policy for lane in model.lane_statistics if lane.hits == maximum]
        if len(leaders) == len(model.lane_statistics):
            return "Current trace result: tie. No policy is universally best."
        if len(leaders) > 1:
            return f"Current trace leaders: {', '.join(leaders)} (tie). This is trace-specific."
        return f"Current trace leader: {leaders[0]}. This does not imply universal superiority."


__all__ = ["StatisticsPanel"]
