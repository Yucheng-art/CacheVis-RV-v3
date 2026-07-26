"""Latest synchronized policy access summary."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ..model import PolicyComparisonStep


class CurrentAccessPanel(QFrame):
    """Render latest execution independently of historical selection."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyCurrentAccessPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Current Access / Latest Execution")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("PolicyCurrentStatus")
        layout.addWidget(self.status_label)
        grid = QGridLayout()
        self.values: dict[str, QLabel] = {}
        fields = (
            ("step", "Step"), ("address", "Address"),
            ("block", "Block"), ("set", "Set"), ("tag", "Tag"),
            ("lanes", "LRU / FIFO / Random"),
            ("divergence", "O / V / S divergence"),
        )
        for index, (key, caption) in enumerate(fields):
            title = QLabel(caption)
            title.setProperty("role", "muted")
            value = QLabel("—")
            value.setObjectName(f"PolicyCurrent_{key}")
            grid.addWidget(title, (index // 5) * 2, index % 5)
            grid.addWidget(value, (index // 5) * 2 + 1, index % 5)
            self.values[key] = value
        layout.addLayout(grid)

    def render(self, step: PolicyComparisonStep | None, *, has_session: bool) -> None:
        if step is None:
            self.status_label.setText(
                "Awaiting first access" if has_session else "Ready"
            )
            for label in self.values.values():
                label.setText("—")
            return
        self.status_label.setText("Latest execution")
        lanes = " / ".join(
            f"{lane.policy} {'HIT' if lane.cache_hit else 'MISS'}"
            for lane in step.lane_steps
        )
        divergence = "  ".join(
            f"{code}={'YES' if active else 'NO'}"
            for code, active in (
                ("O", step.outcome_diverged),
                ("V", step.victim_diverged),
                ("S", step.state_diverged),
            )
        )
        values = {
            "step": str(step.step_index + 1),
            "address": f"{step.address} ({step.address_hex})",
            "block": str(step.block_address),
            "set": str(step.set_index),
            "tag": str(step.tag),
            "lanes": lanes,
            "divergence": divergence,
        }
        for key, value in values.items():
            self.values[key].setText(value)


__all__ = ["CurrentAccessPanel"]
