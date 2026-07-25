"""Cumulative 3C statistics presentation."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ..statistics_view_model import MissTypeStatisticsViewModel


class StatisticsPanel(QFrame):
    """Render authoritative statistics view-model fields."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MissTypeStatisticsPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("3C Statistics")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.grid = QGridLayout()
        self.values: dict[str, QLabel] = {}
        fields = (
            ("accesses", "Accesses"),
            ("hits", "Hits"),
            ("misses", "Misses"),
            ("compulsory", "Compulsory"),
            ("conflict", "Conflict"),
            ("capacity", "Capacity"),
            ("hit_rate_text", "Hit Rate"),
            ("miss_rate_text", "Miss Rate"),
        )
        for index, (key, title) in enumerate(fields):
            card = QFrame()
            card.setObjectName("MissTypeStatisticCard")
            card.setStyleSheet(
                "QFrame#MissTypeStatisticCard { background: #f3f6fa;"
                " border: 1px solid #cbd5e1; border-radius: 6px; }"
                "QFrame#MissTypeStatisticCard QLabel { color: #243447; }"
            )
            card_layout = QVBoxLayout(card)
            label = QLabel(title)
            label.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569;")
            value = QLabel("0")
            value.setObjectName(f"MissTypeStat_{key}")
            value.setStyleSheet("font-size: 18px; font-weight: 800; color: #172a3f;")
            card_layout.addWidget(label)
            card_layout.addWidget(value)
            self.values[key] = value
            self.grid.addWidget(card, index // 4, index % 4)
        layout.addLayout(self.grid)
        self.invariant_label = QLabel("Hits + C + F + A = Accesses")
        self.invariant_label.setObjectName("MissTypeStatisticsInvariant")
        layout.addWidget(self.invariant_label)

    def render(self, model: MissTypeStatisticsViewModel) -> None:
        for key, label in self.values.items():
            label.setText(str(getattr(model, key)))
        self.invariant_label.setText(
            ("✓ " if model.invariant_valid else "⚠ ") + model.invariant_text
        )
