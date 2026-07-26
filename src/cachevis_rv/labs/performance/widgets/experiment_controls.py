"""Sweep input controls and formal definition construction."""

from PySide6.QtCore import Signal
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

from cachevis_rv.experiments.address_trace_parser import parse_address_trace

from ..presets import PERFORMANCE_PRESETS, PerformancePreset
from ..sweep import PerformanceSweepDefinition, PerformanceSweepKind
from .point_editor import PointEditor


SWEEP_PRESETS = tuple(preset for preset in PERFORMANCE_PRESETS if preset.sweep is not None)


class ExperimentControls(QFrame):
    """Collect a complete editable single-level performance sweep."""

    run_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PerformanceExperimentControls")
        layout = QVBoxLayout(self)
        heading = QLabel("Sweep Controls")
        heading.setStyleSheet("font-size: 18px; font-weight: 750;")
        layout.addWidget(heading)

        form = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("PerformancePresetCombo")
        for preset in SWEEP_PRESETS:
            self.preset_combo.addItem(preset.title, preset)
        form.addRow("Preset", self.preset_combo)
        self.trace_input = QTextEdit()
        self.trace_input.setObjectName("PerformanceTraceInput")
        self.trace_input.setMaximumHeight(82)
        self.trace_input.setPlaceholderText("Empty trace is valid; decimal and 0x addresses support comma, space, or newline separators")
        form.addRow("Trace", self.trace_input)
        self.kind_combo = QComboBox()
        for kind in PerformanceSweepKind:
            self.kind_combo.addItem(kind.value.replace("_", " ").title(), kind.value)
        form.addRow("Sweep Kind", self.kind_combo)
        self.baseline_combo = QComboBox()
        form.addRow("Baseline Point", self.baseline_combo)
        layout.addLayout(form)

        self.point_editor = PointEditor()
        layout.addWidget(self.point_editor)
        buttons = QHBoxLayout()
        self.restore_button = QPushButton("Restore Preset")
        self.run_button = QPushButton("Run Sweep")
        self.clear_button = QPushButton("Clear Sweep")
        for button in (self.restore_button, self.run_button, self.clear_button):
            buttons.addWidget(button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.preset_combo.currentIndexChanged.connect(self._preset_changed)
        self.point_editor.table.itemChanged.connect(self._refresh_baseline_ids)
        self.point_editor.add_button.clicked.connect(self._refresh_baseline_ids)
        self.point_editor.remove_button.clicked.connect(self._refresh_baseline_ids)
        self.restore_button.clicked.connect(self.restore_current_preset)
        self.run_button.clicked.connect(self.run_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.apply_preset(self.current_preset())

    def current_preset(self) -> PerformancePreset:
        return self.preset_combo.currentData()

    def _preset_changed(self, _index: int) -> None:
        self.apply_preset(self.current_preset())

    def restore_current_preset(self) -> None:
        self.apply_preset(self.current_preset())

    def apply_preset(self, preset: PerformancePreset) -> None:
        definition = preset.sweep
        if definition is None:
            raise ValueError("the analytical hierarchy example is not a sweep preset")
        self.trace_input.setPlainText(", ".join(str(value) for value in definition.addresses))
        self._select_data(self.kind_combo, definition.kind)
        self.point_editor.load_points(definition.points)
        self._refresh_baseline_ids()
        index = self.baseline_combo.findText(definition.baseline_point_id)
        if index >= 0:
            self.baseline_combo.setCurrentIndex(index)

    def build_definition(self) -> PerformanceSweepDefinition:
        preset = self.current_preset()
        original = preset.sweep
        if original is None:
            raise ValueError("selected preset is not a sweep")
        raw_trace = self.trace_input.toPlainText()
        addresses = () if not raw_trace.strip() else tuple(parse_address_trace(raw_trace))
        points = self.point_editor.build_points()
        if not points:
            raise ValueError("a sweep requires at least one point")
        point_ids = tuple(point.point_id for point in points)
        if any(not point_id for point_id in point_ids):
            raise ValueError("point_id must be a non-empty string")
        if len(set(point_ids)) != len(point_ids):
            raise ValueError("point_id values must be unique within a sweep")
        baseline = self.baseline_combo.currentText().strip()
        if baseline not in point_ids:
            raise ValueError("baseline_point_id must identify an existing point")
        for address in addresses:
            for point in points:
                if address >= 1 << point.config.address_bits:
                    raise ValueError(f"address {address} exceeds the configured address width")
        return PerformanceSweepDefinition(
            sweep_id=original.sweep_id,
            title=original.title,
            description=original.description,
            kind=PerformanceSweepKind(str(self.kind_combo.currentData())),
            addresses=addresses,
            points=points,
            baseline_point_id=baseline,
            expected_teaching_conclusion=original.expected_teaching_conclusion,
        )

    def _refresh_baseline_ids(self, *_args) -> None:
        current = self.baseline_combo.currentText()
        self.baseline_combo.blockSignals(True)
        self.baseline_combo.clear()
        self.baseline_combo.addItems([value for value in self.point_editor.point_ids() if value])
        index = self.baseline_combo.findText(current)
        if index >= 0:
            self.baseline_combo.setCurrentIndex(index)
        self.baseline_combo.blockSignals(False)

    @staticmethod
    def _select_data(combo: QComboBox, value) -> None:
        data = value.value if isinstance(value, PerformanceSweepKind) else value
        index = combo.findData(data)
        if index >= 0:
            combo.setCurrentIndex(index)


__all__ = ["ExperimentControls", "SWEEP_PRESETS"]
