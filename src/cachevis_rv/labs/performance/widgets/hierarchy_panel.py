"""Independent analytical L1/L2 AMAT inputs and result rows."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..hierarchy import TwoLevelTimingModel
from ..presets import ANALYTICAL_L1_L2_MODEL


class HierarchyPanel(QFrame):
    analyze_requested = Signal(object)
    clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceHierarchyPanel")
        layout = QVBoxLayout(self)
        heading = QLabel("Analytical L1/L2 AMAT")
        heading.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(heading)
        note = QLabel("An analytical probability model only — it does not create L2 cache contents.")
        note.setWordWrap(True)
        note.setStyleSheet("background: #fff4d8; color: #5d4510; padding: 8px; border: 1px solid #d4b45d; border-radius: 5px;")
        layout.addWidget(note)
        form = QFormLayout()
        self.l1_hit = self._spin(0.001, 1_000_000, 3)
        self.l1_miss = self._spin(0, 1, 4)
        self.l2_hit = self._spin(0.001, 1_000_000, 3)
        self.l2_local_miss = self._spin(0, 1, 4)
        self.memory_penalty = self._spin(0, 1_000_000, 3)
        for caption, widget in (
            ("L1 Hit Time", self.l1_hit), ("L1 Miss Rate", self.l1_miss),
            ("L2 Hit Time", self.l2_hit), ("L2 Local Miss Rate", self.l2_local_miss),
            ("Memory Penalty", self.memory_penalty),
        ):
            form.addRow(caption, widget)
        layout.addLayout(form)
        buttons = QHBoxLayout()
        self.load_button = QPushButton("Load Example")
        self.analyze_button = QPushButton("Analyze")
        self.clear_button = QPushButton("Clear Hierarchy")
        buttons.addWidget(self.load_button)
        buttons.addWidget(self.analyze_button)
        buttons.addWidget(self.clear_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self.result = QLabel("Load values and choose Analyze. Example AMAT: 3.8 cycles.")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)
        self.load_button.clicked.connect(self.load_example)
        self.analyze_button.clicked.connect(self._analyze)
        self.clear_button.clicked.connect(self.clear_requested)
        self.load_example()

    @staticmethod
    def _spin(minimum, maximum, decimals):
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(decimals)
        return spin

    def load_example(self) -> None:
        model = ANALYTICAL_L1_L2_MODEL
        self.l1_hit.setValue(model.l1_hit_time_cycles)
        self.l1_miss.setValue(model.l1_miss_rate)
        self.l2_hit.setValue(model.l2_hit_time_cycles)
        self.l2_local_miss.setValue(model.l2_local_miss_rate)
        self.memory_penalty.setValue(model.memory_penalty_cycles)

    def _analyze(self) -> None:
        self.analyze_requested.emit(self.build_model())

    def build_model(self) -> TwoLevelTimingModel:
        return TwoLevelTimingModel(
            self.l1_hit.value(), self.l1_miss.value(), self.l2_hit.value(),
            self.l2_local_miss.value(), self.memory_penalty.value(),
        )

    def render(self, model) -> None:
        if model is None:
            self.result.setText("Load values and choose Analyze. Example AMAT: 3.8 cycles.")
            return
        probabilities = "\n".join(f"• {row.label}: {row.probability} ({row.formula})" for row in model.probability_rows)
        contributions = "\n".join(f"• {row.label}: {row.cycles} cycles ({row.formula})" for row in model.contribution_rows)
        path = " → ".join(model.rule_path)
        limits = "\n".join(f"• {note}" for note in model.limitation_notes)
        self.result.setText(
            f"Probability Outcomes\n{probabilities}\nPartition invariant: {'OK' if model.probability_partition_ok else 'CHECK'}\n\n"
            f"Cycle Contributions\n{contributions}\nContribution invariant: {'OK' if model.contribution_sum_ok else 'CHECK'}\n\n"
            f"AMAT = {model.amat_cycles} cycles\nL2 global miss rate = {model.l2_global_miss_rate}\n\n"
            f"Rule Path\n{path}\n\nLocal vs Global\n{model.local_vs_global_explanation}\n\nLimitation Notes\n{limits}"
        )


__all__ = ["HierarchyPanel"]
