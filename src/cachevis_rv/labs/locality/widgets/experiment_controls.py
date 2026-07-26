"""Inputs for creating and advancing a Locality session."""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..presets import LOCALITY_PRESETS, LocalityPreset


class ExperimentControls(QFrame):
    """Collect trace and cache configuration without executing domain logic."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityExperimentControls")
        layout = QVBoxLayout(self)
        heading = QLabel("Experiment Controls")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)

        form = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("LocalityPresetCombo")
        for preset in LOCALITY_PRESETS:
            self.preset_combo.addItem(preset.title, preset)
        form.addRow("Preset", self.preset_combo)

        self.trace_input = QTextEdit()
        self.trace_input.setObjectName("LocalityTraceInput")
        self.trace_input.setMaximumHeight(78)
        self.trace_input.setPlaceholderText(
            "0, 0x4, 8  (commas, spaces, and newlines supported)"
        )
        form.addRow("Address trace", self.trace_input)

        parameters = QHBoxLayout()
        self.cache_size_combo = self._number_combo(
            "LocalityCacheSize", (2, 4, 8, 16, 32, 64, 128)
        )
        self.block_size_combo = self._number_combo(
            "LocalityBlockSize", (1, 2, 4, 8, 16, 32)
        )
        self.ways_combo = self._number_combo(
            "LocalityWays", (1, 2, 4, 8, 16)
        )
        self.policy_combo = QComboBox()
        self.policy_combo.setObjectName("LocalityPolicy")
        for policy in ("LRU", "FIFO", "Random"):
            self.policy_combo.addItem(policy, policy)
        for caption, widget in (
            ("Cache (bytes)", self.cache_size_combo),
            ("Block (bytes)", self.block_size_combo),
            ("Ways", self.ways_combo),
            ("Policy", self.policy_combo),
        ):
            column = QVBoxLayout()
            column.addWidget(QLabel(caption))
            column.addWidget(widget)
            parameters.addLayout(column, 1)
        form.addRow(parameters)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("LocalityResetButton")
        self.step_button = QPushButton("Step")
        self.step_button.setObjectName("LocalityStepButton")
        self.run_all_button = QPushButton("Run All")
        self.run_all_button.setObjectName("LocalityRunAllButton")
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

    def current_preset(self) -> LocalityPreset:
        return self.preset_combo.currentData()

    def apply_preset(self, preset: LocalityPreset) -> None:
        self.trace_input.setPlainText(
            ", ".join(str(address) for address in preset.addresses)
        )
        self._select_data(self.cache_size_combo, preset.config.cache_size_bytes)
        self._select_data(self.block_size_combo, preset.config.block_size_bytes)
        self._select_data(self.ways_combo, preset.config.ways)
        self._select_data(self.policy_combo, preset.config.replacement_policy)

    def input_signature(self) -> tuple[str, int, int, int, str]:
        return (
            self.trace_input.toPlainText(),
            int(self.cache_size_combo.currentData()),
            int(self.block_size_combo.currentData()),
            int(self.ways_combo.currentData()),
            str(self.policy_combo.currentData()),
        )

    @staticmethod
    def _select_data(combo: QComboBox, value) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)


__all__ = ["ExperimentControls"]
