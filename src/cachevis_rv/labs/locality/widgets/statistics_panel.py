"""Cumulative Locality statistics presentation."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ..statistics_view_model import LocalityStatisticsViewModel


class StatisticsPanel(QFrame):
    """Render authoritative statistics with explicit invariant checks."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityStatisticsPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Locality Statistics / Latest Execution")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.grid = QGridLayout()
        self.values: dict[str, QLabel] = {}
        fields = (
            ("accesses", "Accesses"),
            ("hits", "Hits"),
            ("misses", "Misses"),
            ("unique_addresses", "Unique Addresses"),
            ("unique_blocks", "Unique Blocks"),
            ("first_touch_count", "First Touch"),
            ("spatial_count", "Spatial"),
            ("temporal_count", "Temporal"),
            ("same_block_transition_count", "Same-block Transitions"),
            ("hit_rate", "Hit Rate"),
            ("miss_rate", "Miss Rate"),
            ("spatial_event_rate", "Spatial Event Rate"),
            ("temporal_event_rate", "Temporal Event Rate"),
            ("average_address_reuse_gap", "Avg Address Reuse Gap"),
            ("average_block_reuse_gap", "Avg Block Reuse Gap"),
            ("average_block_reuse_distance", "Avg Block Reuse Distance"),
        )
        for index, (key, title) in enumerate(fields):
            card = QFrame()
            card.setObjectName("LocalityStatisticCard")
            card.setStyleSheet(
                "QFrame#LocalityStatisticCard { background: #f3f6fa;"
                " border: 1px solid #cbd5e1; border-radius: 6px; }"
                "QFrame#LocalityStatisticCard QLabel { color: #243447; }"
            )
            card_layout = QVBoxLayout(card)
            title_label = QLabel(title)
            title_label.setStyleSheet(
                "font-size: 10px; font-weight: 700; color: #475569;"
            )
            value = QLabel("0")
            value.setObjectName(f"LocalityStat_{key}")
            value.setStyleSheet(
                "font-size: 17px; font-weight: 800; color: #172a3f;"
            )
            card_layout.addWidget(title_label)
            card_layout.addWidget(value)
            self.values[key] = value
            self.grid.addWidget(card, index // 4, index % 4)
        layout.addLayout(self.grid)
        self.invariant_label = QLabel()
        self.invariant_label.setObjectName("LocalityStatisticsInvariants")
        self.invariant_label.setWordWrap(True)
        layout.addWidget(self.invariant_label)

    def render(self, model: LocalityStatisticsViewModel) -> None:
        rate_fields = {
            "hit_rate", "miss_rate", "spatial_event_rate", "temporal_event_rate"
        }
        average_fields = {
            "average_address_reuse_gap",
            "average_block_reuse_gap",
            "average_block_reuse_distance",
        }
        for key, label in self.values.items():
            value = getattr(model, key)
            if key in rate_fields:
                text = f"{value:.1%}"
            elif key in average_fields:
                text = "N/A" if value is None else f"{value:.2f}"
            else:
                text = str(value)
            label.setText(text)
        checks = (
            ("F + S + T = Accesses", model.partition_invariant_ok),
            ("F + S = Unique Addresses", model.address_invariant_ok),
            ("Hits + Misses = Accesses", model.cache_invariant_ok),
        )
        self.invariant_label.setText(
            "   ".join(("✓ " if valid else "⚠ ") + text for text, valid in checks)
        )


__all__ = ["StatisticsPanel"]
