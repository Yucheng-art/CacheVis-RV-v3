"""Inputs for synchronized replacement-policy experiments."""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..presets import POLICY_PRESETS, PolicyPreset


class ExperimentControls(QFrame):
    """Collect trace, cache geometry, and Random replay seed."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyExperimentControls")
        layout = QVBoxLayout(self)
        heading = QLabel("Experiment Controls")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)

        strategy_note = QLabel(
            "Synchronized policies:  LRU   |   FIFO   |   Random (seeded replay)"
        )
        strategy_note.setObjectName("PolicyStrategyNote")
        strategy_note.setStyleSheet(
            "background: #e8eef6; color: #20364d; border: 1px solid #8ba2ba;"
            "border-radius: 6px; padding: 7px; font-weight: 700;"
        )
        layout.addWidget(strategy_note)

        form = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("PolicyPresetCombo")
        for preset in POLICY_PRESETS:
            self.preset_combo.addItem(preset.title, preset)
        form.addRow("Preset", self.preset_combo)

        self.trace_input = QTextEdit()
        self.trace_input.setObjectName("PolicyTraceInput")
        self.trace_input.setMaximumHeight(82)
        self.trace_input.setPlaceholderText(
            "0, 0x4, 8  (commas, spaces, and newlines supported)"
        )
        form.addRow("Address trace", self.trace_input)

        parameters = QHBoxLayout()
        self.cache_size_combo = self._number_combo(
            "PolicyCacheSize", (2, 4, 8, 16, 32, 64, 128)
        )
        self.block_size_combo = self._number_combo(
            "PolicyBlockSize", (1, 2, 4, 8, 16, 32)
        )
        self.ways_combo = self._number_combo(
            "PolicyWays", (1, 2, 4, 8, 16)
        )
        self.seed_input = QLineEdit()
        self.seed_input.setObjectName("PolicyRandomSeed")
        self.seed_input.setPlaceholderText("Integer seed")
        for caption, widget in (
            ("Cache (bytes)", self.cache_size_combo),
            ("Block (bytes)", self.block_size_combo),
            ("Ways", self.ways_combo),
            ("Random seed", self.seed_input),
        ):
            column = QVBoxLayout()
            column.addWidget(QLabel(caption))
            column.addWidget(widget)
            parameters.addLayout(column, 1)
        form.addRow(parameters)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("PolicyResetButton")
        self.step_button = QPushButton("Step")
        self.step_button.setObjectName("PolicyStepButton")
        self.run_all_button = QPushButton("Run All")
        self.run_all_button.setObjectName("PolicyRunAllButton")
        for button in (self.reset_button, self.step_button, self.run_all_button):
            buttons.addWidget(button)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self.apply_preset(self.current_preset())

    @staticmethod
    def _number_combo(name: str, values: tuple[int, ...]) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName(name)
        for value in values:
            combo.addItem(str(value), value)
        return combo

    def current_preset(self) -> PolicyPreset:
        return self.preset_combo.currentData()

    def apply_preset(self, preset: PolicyPreset) -> None:
        self.trace_input.setPlainText(
            ", ".join(str(address) for address in preset.addresses)
        )
        self._select_data(self.cache_size_combo, preset.config.cache_size_bytes)
        self._select_data(self.block_size_combo, preset.config.block_size_bytes)
        self._select_data(self.ways_combo, preset.config.ways)
        self.seed_input.setText(str(preset.random_seed))

    def input_signature(self) -> tuple[str, int, int, int, str]:
        return (
            self.trace_input.toPlainText(),
            int(self.cache_size_combo.currentData()),
            int(self.block_size_combo.currentData()),
            int(self.ways_combo.currentData()),
            self.seed_input.text().strip(),
        )

    @staticmethod
    def _select_data(combo: QComboBox, value: int) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)


__all__ = ["ExperimentControls"]
