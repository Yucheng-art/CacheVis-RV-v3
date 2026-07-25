"""Address & Cache Visualizer tab for the PySide6 GUI."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from address_bit_bar import AddressBitBarWidget
from address_trace_parser import parse_address_trace
from cache_contents_widget import CacheContentsWidget
from cache_config import CacheConfig
from explanation_panel_widget import ExplanationPanelWidget
from step_summary_widget import StepSummaryWidget
from timeline_widget import AccessTimelineWidget
from visualizer_model import AccessStepViewModel, CacheLineViewModel
from visualizer_step_engine import VisualizerStepEngine


DEMO_PRESETS = {
    "Dan-style LRU demo": {
        "addresses": "0 2 0 1 4 0",
        "cache_size": "4",
        "block_size": "1",
        "ways": "2",
        "policy": "LRU",
    },
    "Direct-mapped conflict demo": {
        "addresses": "0 4 0 4",
        "cache_size": "4",
        "block_size": "1",
        "ways": "1",
        "policy": "LRU",
    },
    "Spatial locality demo": {
        "addresses": "0 1 2 3 4 5 6 7",
        "cache_size": "8",
        "block_size": "4",
        "ways": "1",
        "policy": "LRU",
    },
    "Hex address demo": {
        "addresses": "0x14 0x1c 0x34 0x8014",
        "cache_size": "16384",
        "block_size": "16",
        "ways": "1",
        "policy": "LRU",
    },
}


class AddressVisualizerWidget(QWidget):
    """Interactive single-step address and cache visualizer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.engine: VisualizerStepEngine | None = None
        self.last_step: AccessStepViewModel | None = None
        self._info_labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(10)

        main = QSplitter(Qt.Orientation.Horizontal)
        main.addWidget(self._build_config_panel())
        main.addWidget(self._build_center_panel())
        main.addWidget(self._build_explanation_panel())
        main.setStretchFactor(0, 0)
        main.setStretchFactor(1, 1)
        main.setStretchFactor(2, 0)
        main.setSizes([320, 760, 400])
        root.addWidget(main, 1)
        root.addWidget(self._build_bottom_panel(), 0)

    def _build_config_panel(self) -> QGroupBox:
        group = QGroupBox("Experiment Controls")
        group.setMinimumWidth(300)
        group.setMaximumWidth(360)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        form = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(DEMO_PRESETS.keys())
        self.preset_combo.currentTextChanged.connect(self.apply_demo_preset)
        form.addRow("Demo preset", self.preset_combo)

        self.address_input = QTextEdit()
        self.address_input.setPlainText("0 2 0 1 4 0")
        self.address_input.setFixedHeight(120)
        form.addRow("Address sequence", self.address_input)

        self.cache_size_combo = QComboBox()
        self.cache_size_combo.addItems(
            ["4", "8", "16", "32", "64", "128", "256", "4096", "8192", "16384"]
        )
        self.cache_size_combo.setCurrentText("4")
        form.addRow("Cache size", self.cache_size_combo)

        self.block_size_combo = QComboBox()
        self.block_size_combo.addItems(["1", "2", "4", "8", "16", "32"])
        self.block_size_combo.setCurrentText("1")
        form.addRow("Block size", self.block_size_combo)

        self.ways_combo = QComboBox()
        self.ways_combo.addItems(["1", "2", "4", "8"])
        self.ways_combo.setCurrentText("2")
        form.addRow("Ways", self.ways_combo)

        self.policy_combo = QComboBox()
        self.policy_combo.addItems(["LRU", "FIFO", "Random"])
        form.addRow("Replacement policy", self.policy_combo)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_visualizer)
        buttons.addWidget(self.reset_button)

        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.step_once)
        buttons.addWidget(self.step_button)

        self.run_all_button = QPushButton("Run All")
        self.run_all_button.clicked.connect(self.run_all)
        buttons.addWidget(self.run_all_button)
        layout.addLayout(buttons)
        hint = QLabel(
            "Reset builds a fresh cache. Step advances one address. Run All "
            "finishes the current sequence without animation."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)
        self.apply_demo_preset(self.preset_combo.currentText())
        return group

    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.addWidget(self._build_current_address_panel(), 0)
        layout.addWidget(self._build_address_bits_panel(), 0)
        layout.addWidget(self._build_cache_table_panel(), 1)
        return panel

    def _build_current_address_panel(self) -> QGroupBox:
        group = QGroupBox("Current Address")
        grid = QGridLayout(group)
        fields = [
            ("step_index", "Step index"),
            ("address_dec", "Address decimal"),
            ("address_hex", "Address hex"),
            ("address_binary", "Address binary"),
            ("tag_bits", "Tag bits"),
            ("index_bits", "Index bits"),
            ("offset_bits", "Offset bits"),
            ("tag", "Tag value"),
            ("index", "Index value"),
            ("offset", "Offset value"),
            ("mapped_set", "Mapped set"),
        ]
        for row, (key, title) in enumerate(fields):
            label = QLabel("-")
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            if key == "address_binary":
                label.setWordWrap(True)
                label.setStyleSheet("font-family: Consolas, monospace;")
            self._info_labels[key] = label
            grid.addWidget(QLabel(title), row // 2, (row % 2) * 2)
            grid.addWidget(label, row // 2, (row % 2) * 2 + 1)
        return group

    def _build_address_bits_panel(self) -> QGroupBox:
        group = QGroupBox("Tag / Index / Offset Split")
        layout = QVBoxLayout(group)
        legend = QLabel(
            "Offset selects byte/word inside the block. Index selects the cache "
            "set/row. Tag checks whether the selected line contains the target block.\n"
            "Offset: selects the position inside the block. "
            "Index: selects the cache set / row. "
            "Tag: confirms whether this line stores the target memory block."
        )
        legend.setWordWrap(True)
        layout.addWidget(legend)

        self.address_bit_bar = AddressBitBarWidget()
        layout.addWidget(self.address_bit_bar)
        return group

    def _build_cache_table_panel(self) -> QGroupBox:
        group = QGroupBox("Cache Contents")
        layout = QVBoxLayout(group)
        self.cache_contents = CacheContentsWidget()
        layout.addWidget(self.cache_contents)
        return group

    def _build_explanation_panel(self) -> ExplanationPanelWidget:
        self.explanation_panel = ExplanationPanelWidget()
        return self.explanation_panel

    def _build_step_summary_panel(self) -> StepSummaryWidget:
        self.step_summary = StepSummaryWidget()
        return self.step_summary

    def _build_timeline_panel(self) -> AccessTimelineWidget:
        self.timeline_widget = AccessTimelineWidget()
        return self.timeline_widget

    def _build_bottom_panel(self) -> QSplitter:
        bottom = QSplitter(Qt.Orientation.Horizontal)
        bottom.addWidget(self._build_step_summary_panel())
        timeline_panel = self._build_timeline_panel()
        timeline_panel.step_selected.connect(self._show_step_summary_for_step)
        bottom.addWidget(timeline_panel)
        bottom.setStretchFactor(0, 0)
        bottom.setStretchFactor(1, 1)
        bottom.setSizes([420, 760])
        return bottom

    def apply_demo_preset(self, preset_name: str) -> None:
        """Fill the controls from a named demo without executing the trace."""
        preset = DEMO_PRESETS.get(preset_name)
        if not preset:
            return
        self.address_input.setPlainText(preset["addresses"])
        self.cache_size_combo.setCurrentText(preset["cache_size"])
        self.block_size_combo.setCurrentText(preset["block_size"])
        self.ways_combo.setCurrentText(preset["ways"])
        self.policy_combo.setCurrentText(preset["policy"])
        self.engine = None
        self.last_step = None
        if hasattr(self, "timeline_widget"):
            self.timeline_widget.clear()
            self.step_summary.clear()
            self._clear_current_address()
            self._clear_address_segments()
            self.cache_contents.clear()
            self.explanation_panel.show_placeholder(
                "Preset loaded. Click Reset to build a fresh cache."
            )

    def reset_visualizer(self) -> None:
        """Read settings, create a fresh engine, and display an empty cache."""
        self.engine = None
        self.last_step = None
        try:
            config = self._read_config()
            addresses = parse_address_trace(self.address_input.toPlainText())
            self.engine = VisualizerStepEngine(config, addresses)
        except Exception as exc:
            QMessageBox.warning(self, "Address Visualizer Error", str(exc))
            return

        self.timeline_widget.clear()
        self.step_summary.clear()
        self._clear_current_address()
        self._clear_address_segments()
        self.explanation_panel.show_placeholder("Ready. Click Step to access the first address.")
        self._update_cache_table(
            _snapshot_to_line_models(self.engine.simulator.get_cache_snapshot()),
            mapped_set=None,
            hit_way=None,
            victim_way=None,
            replacement_reason=None,
        )

    def step_once(self) -> None:
        """Execute one access and update all visualizer panels."""
        if self.engine is None:
            self.reset_visualizer()
            if self.engine is None:
                return

        if not self.engine.has_next():
            QMessageBox.information(self, "Address Visualizer", "All addresses are complete.")
            return

        try:
            step = self.engine.step()
        except Exception as exc:
            QMessageBox.warning(self, "Address Visualizer Error", str(exc))
            return
        self._display_step(step)

    def run_all(self) -> None:
        """Run the remaining trace immediately and show the final state."""
        if self.engine is None:
            self.reset_visualizer()
            if self.engine is None:
                return

        ran_any = False
        while self.engine.has_next():
            try:
                step = self.engine.step()
            except Exception as exc:
                QMessageBox.warning(self, "Address Visualizer Error", str(exc))
                return
            self._display_step(step)
            ran_any = True

        if not ran_any:
            QMessageBox.information(self, "Address Visualizer", "All addresses are complete.")

    def _read_config(self) -> CacheConfig:
        return CacheConfig(
            cache_size_bytes=int(self.cache_size_combo.currentText()),
            block_size_bytes=int(self.block_size_combo.currentText()),
            ways=int(self.ways_combo.currentText()),
            replacement_policy=self.policy_combo.currentText(),
        )

    def _display_step(self, step: AccessStepViewModel) -> None:
        self.last_step = step
        self._update_current_address(step)
        self._update_address_segments(step)
        self._update_cache_table(
            step.after_cache_snapshot,
            mapped_set=step.mapped_set,
            hit_way=step.hit_way,
            victim_way=step.victim_way,
            replacement_reason=step.replacement_reason,
        )
        self.explanation_panel.set_step(step)
        self.timeline_widget.add_step(step)
        self.step_summary.set_step(step)

    def _show_step_summary_for_step(self, step_index: int) -> None:
        step = self.timeline_widget.get_step(step_index)
        if step is not None:
            self.step_summary.set_step(step)

    def _update_current_address(self, step: AccessStepViewModel) -> None:
        values = {
            "step_index": str(step.step_index),
            "address_dec": step.address_dec,
            "address_hex": step.address_hex,
            "address_binary": step.address_binary,
            "tag_bits": str(step.tag_bits),
            "index_bits": str(step.index_bits),
            "offset_bits": str(step.offset_bits),
            "tag": str(step.tag),
            "index": str(step.index),
            "offset": str(step.offset),
            "mapped_set": str(step.mapped_set),
        }
        for key, value in values.items():
            self._info_labels[key].setText(value)

    def _clear_current_address(self) -> None:
        for label in self._info_labels.values():
            label.setText("-")

    def _update_address_segments(self, step: AccessStepViewModel) -> None:
        self.address_bit_bar.set_address(
            address_binary=step.address_binary,
            tag_bits=step.tag_bits,
            index_bits=step.index_bits,
            offset_bits=step.offset_bits,
            tag=step.tag,
            index=step.index,
            offset=step.offset,
        )

    def _clear_address_segments(self) -> None:
        self.address_bit_bar.clear()

    def _update_cache_table(
        self,
        snapshot: list[list[CacheLineViewModel]],
        *,
        mapped_set: int | None,
        hit_way: int | None,
        victim_way: int | None,
        replacement_reason: str | None,
    ) -> None:
        self.cache_contents.set_cache_snapshot(
            snapshot,
            mapped_set=mapped_set,
            hit_way=hit_way,
            victim_way=victim_way,
            replacement_reason=replacement_reason,
        )

def _snapshot_to_line_models(snapshot: list[list[dict]]) -> list[list[CacheLineViewModel]]:
    return [
        [
            CacheLineViewModel(
                set_index=int(line["set_index"]),
                way_index=int(line["way"]),
                valid=bool(line["valid"]),
                tag=line["tag"],
                dirty=bool(line["dirty"]),
                last_used=int(line["last_used"]),
                insert_time=int(line["insert_time"]),
            )
            for line in cache_set
        ]
        for cache_set in snapshot
    ]
