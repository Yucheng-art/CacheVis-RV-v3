"""Editable inputs and lifecycle controls for write-policy experiments."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QTextEdit, QVBoxLayout, QWidget,
)

from cachevis_rv.core import CacheConfig

from ..model import MemoryAccessKind, WriteTrafficAssumptions
from ..parser import parse_memory_access_trace
from ..presets import WRITE_POLICY_PRESETS
from .common import section_frame


def _trace_text(accesses) -> str:
    return ", ".join(
        f"{'R' if access.kind is MemoryAccessKind.READ else 'W'} 0x{access.address:x}"
        for access in accesses
    )


class ExperimentControls(QWidget):
    load_requested = Signal()
    reset_requested = Signal()
    step_requested = Signal()
    run_all_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        frame, outer = section_frame("Experiment Controls")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(frame)

        form_host = QWidget()
        form = QGridLayout(form_host)
        form.setContentsMargins(0, 0, 0, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("WritePolicyPresetCombo")
        for preset in WRITE_POLICY_PRESETS:
            self.preset_combo.addItem(preset.title, preset)
        form.addWidget(QLabel("Preset"), 0, 0)
        form.addWidget(self.preset_combo, 0, 1, 1, 3)

        self.cache_size_input = self._spin(1, 1 << 30)
        self.block_size_input = self._spin(1, 1 << 20)
        self.ways_input = self._spin(1, 1 << 16)
        self.address_bits_input = self._spin(1, 64)
        self.store_size_input = self._spin(1, 1 << 20)
        self.policy_combo = QComboBox()
        self.policy_combo.addItems(("LRU", "FIFO"))
        fields = (
            ("Cache Size (B)", self.cache_size_input),
            ("Block Size (B)", self.block_size_input),
            ("Ways", self.ways_input),
            ("Replacement", self.policy_combo),
            ("Address Bits", self.address_bits_input),
            ("Store Size (B)", self.store_size_input),
        )
        for index, (label, editor) in enumerate(fields):
            row = 1 + index // 2
            column = (index % 2) * 2
            form.addWidget(QLabel(label), row, column)
            form.addWidget(editor, row, column + 1)
        outer.addWidget(form_host)

        note = QLabel("Replacement is limited to LRU/FIFO here. Use Policy Lab to study Random replacement.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #a9bad0;")
        outer.addWidget(note)
        self.trace_input = QTextEdit()
        self.trace_input.setObjectName("WritePolicyTraceInput")
        self.trace_input.setMaximumHeight(100)
        self.trace_input.setPlaceholderText(
            "Examples: R 0x0, W 16, R:32. Empty trace is valid."
        )
        outer.addWidget(QLabel("Read / Write Trace"))
        outer.addWidget(self.trace_input)

        buttons = QHBoxLayout()
        self.restore_button = QPushButton("Restore Preset")
        self.load_button = QPushButton("Load Experiment")
        self.reset_button = QPushButton("Reset")
        self.step_button = QPushButton("Step")
        self.run_all_button = QPushButton("Run All")
        self.clear_button = QPushButton("Clear")
        for button in (
            self.restore_button, self.load_button, self.reset_button,
            self.step_button, self.run_all_button, self.clear_button,
        ):
            buttons.addWidget(button)
        buttons.addStretch(1)
        outer.addLayout(buttons)
        self.error_label = QLabel("")
        self.error_label.setObjectName("WritePolicyInputError")
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #ffb4ab; font-weight: 700;")
        outer.addWidget(self.error_label)

        self.preset_combo.currentIndexChanged.connect(self._preset_changed)
        self.restore_button.clicked.connect(self.restore_current_preset)
        self.load_button.clicked.connect(self.load_requested)
        self.reset_button.clicked.connect(self.reset_requested)
        self.step_button.clicked.connect(self.step_requested)
        self.run_all_button.clicked.connect(self.run_all_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.apply_preset(self.current_preset())
        self.render_state(None)

    @staticmethod
    def _spin(minimum, maximum):
        editor = QSpinBox()
        editor.setRange(minimum, maximum)
        return editor

    def current_preset(self):
        return self.preset_combo.currentData()

    def _preset_changed(self, _index: int) -> None:
        self.apply_preset(self.current_preset())

    def restore_current_preset(self) -> None:
        self.apply_preset(self.current_preset())

    def apply_preset(self, preset) -> None:
        config = preset.config
        self.cache_size_input.setValue(config.cache_size_bytes)
        self.block_size_input.setValue(config.block_size_bytes)
        self.ways_input.setValue(config.ways)
        self.address_bits_input.setValue(config.address_bits)
        self.store_size_input.setValue(preset.assumptions.store_size_bytes)
        index = self.policy_combo.findText(config.replacement_policy)
        self.policy_combo.setCurrentIndex(max(index, 0))
        self.trace_input.setPlainText(_trace_text(preset.accesses))
        self.set_error("")

    def build_inputs(self):
        replacement = self.policy_combo.currentText()
        if replacement not in {"LRU", "FIFO"}:
            raise ValueError("Write Policy Lab supports only LRU or FIFO replacement")
        config = CacheConfig(
            cache_size_bytes=self.cache_size_input.value(),
            block_size_bytes=self.block_size_input.value(),
            ways=self.ways_input.value(),
            replacement_policy=replacement,
            address_bits=self.address_bits_input.value(),
        )
        assumptions = WriteTrafficAssumptions(self.store_size_input.value())
        accesses = parse_memory_access_trace(self.trace_input.toPlainText())
        return config, accesses, assumptions

    def render_state(self, state) -> None:
        loaded = bool(state is not None and state.has_experiment)
        has_next = loaded and not state.is_complete
        self.reset_button.setEnabled(loaded)
        self.step_button.setEnabled(has_next)
        self.run_all_button.setEnabled(has_next)
        self.clear_button.setEnabled(loaded)

    def set_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(bool(message))


__all__ = ["ExperimentControls"]
