"""Input controls for creating and advancing a Miss Type session."""

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

from ..presets import MISS_TYPE_PRESETS, MissTypePreset


class ExperimentControls(QFrame):
    """Collect trace/configuration input without executing domain logic."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MissTypeExperimentControls")
        layout = QVBoxLayout(self)
        heading = QLabel("Experiment Controls")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)

        form = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("MissTypePresetCombo")
        for preset in MISS_TYPE_PRESETS:
            self.preset_combo.addItem(preset.name, preset)
        form.addRow("Preset", self.preset_combo)

        self.trace_input = QTextEdit()
        self.trace_input.setObjectName("MissTypeTraceInput")
        self.trace_input.setMaximumHeight(76)
        self.trace_input.setPlaceholderText("0, 0x4, 8  (commas, spaces, and newlines supported)")
        form.addRow("Address trace", self.trace_input)

        parameters = QHBoxLayout()
        self.cache_size_combo = self._number_combo(
            "MissTypeCacheSize", (2, 4, 8, 16, 32, 64)
        )
        self.block_size_combo = self._number_combo(
            "MissTypeBlockSize", (1, 2, 4, 8, 16)
        )
        self.ways_combo = self._number_combo("MissTypeWays", (1, 2, 4, 8, 16))
        self.policy_combo = QComboBox()
        self.policy_combo.setObjectName("MissTypePolicy")
        self.policy_combo.addItem("LRU", "LRU")
        self.policy_combo.setEnabled(False)
        self.policy_combo.setToolTip(
            "The foundational 3C model uses a same-capacity fully associative "
            "LRU reference cache, so the actual cache is fixed to LRU."
        )
        for label, widget in (
            ("Cache (bytes)", self.cache_size_combo),
            ("Block (bytes)", self.block_size_combo),
            ("Ways", self.ways_combo),
            ("Policy", self.policy_combo),
        ):
            column = QVBoxLayout()
            column.addWidget(QLabel(label))
            column.addWidget(widget)
            parameters.addLayout(column, 1)
        form.addRow(parameters)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("MissTypeResetButton")
        self.step_button = QPushButton("Step")
        self.step_button.setObjectName("MissTypeStepButton")
        self.run_all_button = QPushButton("Run All")
        self.run_all_button.setObjectName("MissTypeRunAllButton")
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

    def current_preset(self) -> MissTypePreset:
        return self.preset_combo.currentData()

    def apply_preset(self, preset: MissTypePreset) -> None:
        self.trace_input.setPlainText(", ".join(str(value) for value in preset.addresses))
        self._select_data(self.cache_size_combo, preset.config.cache_size_bytes)
        self._select_data(self.block_size_combo, preset.config.block_size_bytes)
        self._select_data(self.ways_combo, preset.config.ways)

    def input_signature(self) -> tuple[str, int, int, int]:
        return (
            self.trace_input.toPlainText(),
            int(self.cache_size_combo.currentData()),
            int(self.block_size_combo.currentData()),
            int(self.ways_combo.currentData()),
        )

    @staticmethod
    def _select_data(combo: QComboBox, value: int) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)
