"""Current/latest access summary panel."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ..model import MissTypeStep


class CurrentAccessPanel(QFrame):
    """Render the latest actual execution, independently of history selection."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MissTypeCurrentAccessPanel")
        layout = QVBoxLayout(self)
        title = QLabel("Current Access / Latest Result")
        title.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(title)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("MissTypeCurrentStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.grid = QGridLayout()
        self.value_labels: dict[str, QLabel] = {}
        fields = (
            ("step", "Step"),
            ("address", "Address"),
            ("block", "Memory block"),
            ("actual", "Actual Cache"),
            ("reference", "Reference Cache"),
            ("classification", "Classification"),
            ("actual_location", "Actual location"),
            ("reference_location", "Reference location"),
        )
        for index, (key, caption) in enumerate(fields):
            label = QLabel(caption)
            label.setProperty("role", "muted")
            value = QLabel("—")
            value.setObjectName(f"MissTypeCurrent_{key}")
            self.grid.addWidget(label, index // 4 * 2, index % 4)
            self.grid.addWidget(value, index // 4 * 2 + 1, index % 4)
            self.value_labels[key] = value
        layout.addLayout(self.grid)

    def render(self, step: MissTypeStep | None, *, has_session: bool) -> None:
        if step is None:
            self.status_label.setText(
                "Awaiting first access" if has_session else "Ready"
            )
            for label in self.value_labels.values():
                label.setText("—")
            return
        self.status_label.setText("Latest actual execution")
        classification = (
            "HIT" if step.actual_result == "hit" else step.miss_type.value.upper()
        )
        values = {
            "step": str(step.step_index + 1),
            "address": f"{step.address} (0x{step.address:X})",
            "block": str(step.block_address),
            "actual": step.actual_result.upper(),
            "reference": step.reference_result.upper(),
            "classification": classification,
            "actual_location": self._location(
                step.actual_set_index, step.actual_hit_way, step.actual_victim_way
            ),
            "reference_location": self._location(
                step.reference_set_index,
                step.reference_hit_way,
                step.reference_victim_way,
            ),
        }
        for key, text in values.items():
            self.value_labels[key].setText(text)

    @staticmethod
    def _location(set_index, hit_way, victim_way) -> str:
        if set_index is None:
            return "—"
        if hit_way is not None:
            return f"Set {set_index}, hit way {hit_way}"
        if victim_way is not None:
            return f"Set {set_index}, fill/victim way {victim_way}"
        return f"Set {set_index}"
