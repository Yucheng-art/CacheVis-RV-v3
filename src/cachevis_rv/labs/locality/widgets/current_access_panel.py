"""Latest executed Locality access summary."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ..model import LocalityStep


class CurrentAccessPanel(QFrame):
    """Render current execution independently of selected historical evidence."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityCurrentAccessPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Current Access / Latest Execution")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("LocalityCurrentStatus")
        layout.addWidget(self.status_label)
        self.grid = QGridLayout()
        self.values: dict[str, QLabel] = {}
        fields = (
            ("step", "Step"),
            ("address", "Address"),
            ("block", "Block"),
            ("offset", "Offset"),
            ("kind", "Primary evidence"),
            ("cache", "Cache result"),
            ("set", "Actual set"),
            ("way", "Hit / victim way"),
            ("delta", "Address delta"),
            ("same_block", "Same block as previous"),
        )
        for index, (key, caption) in enumerate(fields):
            title = QLabel(caption)
            title.setProperty("role", "muted")
            value = QLabel("—")
            value.setObjectName(f"LocalityCurrent_{key}")
            self.grid.addWidget(title, (index // 5) * 2, index % 5)
            self.grid.addWidget(value, (index // 5) * 2 + 1, index % 5)
            self.values[key] = value
        layout.addLayout(self.grid)

    def render(self, step: LocalityStep | None, *, has_session: bool) -> None:
        if step is None:
            self.status_label.setText(
                "Awaiting first access" if has_session else "Ready"
            )
            for label in self.values.values():
                label.setText("—")
            return
        self.status_label.setText("Latest execution")
        way = (
            f"Hit way {step.hit_way}"
            if step.hit_way is not None
            else f"Victim/fill way {step.victim_way}"
        )
        values = {
            "step": str(step.step_index + 1),
            "address": f"{step.address} ({step.address_hex})",
            "block": str(step.block_address),
            "offset": str(step.offset),
            "kind": step.locality_kind.value.replace("_", " ").title(),
            "cache": step.cache_result.upper(),
            "set": str(step.set_index),
            "way": way,
            "delta": "N/A" if step.evidence.address_delta is None else str(
                step.evidence.address_delta
            ),
            "same_block": "Yes" if step.evidence.same_block_as_previous else "No",
        }
        for key, text in values.items():
            self.values[key].setText(text)


__all__ = ["CurrentAccessPanel"]
