"""Scrollable Locality Lab page orchestration."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from cachevis_rv.core import CacheConfig
from cachevis_rv.experiments.address_trace_parser import parse_address_trace

from ..controller import LocalityController
from ..page_state import LocalityPageState
from .block_access_map import BlockAccessMap
from .cache_panel import CachePanel
from .current_access_panel import CurrentAccessPanel
from .evidence_panel import EvidencePanel
from .experiment_controls import ExperimentControls
from .statistics_panel import StatisticsPanel
from .timeline import LocalityTimeline


class LocalityLabWidget(QScrollArea):
    """Complete teaching page backed exclusively by LocalityController."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("LocalityLabWidget")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.controller = LocalityController()
        self._session_signature: tuple[str, int, int, int, str] | None = None
        self._build_ui()
        self._connect_signals()
        self._update_teaching_card()
        self._render(self.controller.state)

    def _build_ui(self) -> None:
        content = QWidget()
        content.setObjectName("LocalityLabContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 30)
        layout.setSpacing(16)

        title = QLabel("Locality Lab")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        subtitle = QLabel(
            "Follow each address through block/offset mapping, trace-history "
            "evidence, reuse metrics, and the independent cache result."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("role", "muted")
        layout.addWidget(subtitle)

        self.concept_note = QLabel(
            "F / S / T are mutually exclusive primary evidence categories for "
            "teaching. Real accesses can exhibit multiple locality properties. "
            "A cache HIT does not automatically mean Temporal, and a cache MISS "
            "does not mean locality is absent."
        )
        self.concept_note.setWordWrap(True)
        self.concept_note.setObjectName("LocalityConceptNote")
        self.concept_note.setStyleSheet(
            "background: #e8eef6; color: #20364d; border: 1px solid #8ba2ba;"
            "border-radius: 7px; padding: 10px;"
        )
        layout.addWidget(self.concept_note)

        self.controls = ExperimentControls()
        layout.addWidget(self.controls)
        self.current_panel = CurrentAccessPanel()
        layout.addWidget(self.current_panel)

        middle = QGridLayout()
        self.evidence_panel = EvidencePanel()
        self.cache_panel = CachePanel()
        middle.addWidget(self.evidence_panel, 0, 0)
        middle.addWidget(self.cache_panel, 0, 1)
        middle.setColumnStretch(0, 1)
        middle.setColumnStretch(1, 1)
        layout.addLayout(middle)

        self.block_access_map = BlockAccessMap()
        layout.addWidget(self.block_access_map)

        lower = QGridLayout()
        self.statistics_panel = StatisticsPanel()
        lower.addWidget(self.statistics_panel, 0, 0)
        self.teaching_panel = self._build_teaching_panel()
        lower.addWidget(self.teaching_panel, 0, 1)
        lower.setColumnStretch(0, 2)
        lower.setColumnStretch(1, 1)
        layout.addLayout(lower)

        self.timeline = LocalityTimeline()
        layout.addWidget(self.timeline)
        layout.addStretch(1)
        self.setWidget(content)

    def _build_teaching_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("LocalityPresetTeachingPanel")
        panel.setStyleSheet(
            "QFrame#LocalityPresetTeachingPanel { background: #f7f2ff;"
            " border: 1px solid #a78bca; border-radius: 8px; }"
            "QFrame#LocalityPresetTeachingPanel QLabel { color: #3f2768; }"
        )
        layout = QVBoxLayout(panel)
        heading = QLabel("Teaching Insight")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.preset_title_label = QLabel()
        self.preset_title_label.setStyleSheet("font-weight: 800;")
        layout.addWidget(self.preset_title_label)
        self.preset_description_label = QLabel()
        self.preset_description_label.setWordWrap(True)
        layout.addWidget(self.preset_description_label)
        self.preset_conclusion_label = QLabel()
        self.preset_conclusion_label.setWordWrap(True)
        layout.addWidget(self.preset_conclusion_label)
        self.matrix_hint_label = QLabel(
            "Same addresses, same F/S counts, different order, different Cache result."
        )
        self.matrix_hint_label.setWordWrap(True)
        self.matrix_hint_label.setStyleSheet("font-weight: 750;")
        layout.addWidget(self.matrix_hint_label)
        return panel

    def _connect_signals(self) -> None:
        self.controls.preset_combo.currentIndexChanged.connect(
            self._preset_changed
        )
        self.controls.reset_button.clicked.connect(self.reset_experiment)
        self.controls.step_button.clicked.connect(self.step_experiment)
        self.controls.run_all_button.clicked.connect(self.run_all_experiment)
        self.timeline.step_selected.connect(self.select_timeline_step)

    def _preset_changed(self, _index: int) -> None:
        self.controls.apply_preset(self.controls.current_preset())
        self._session_signature = None
        self._update_teaching_card()
        self._render(self.controller.clear_session())

    def reset_experiment(self) -> bool:
        return self._start_from_inputs() is not None

    def step_experiment(self) -> bool:
        if not self._ensure_current_session():
            return False
        if self.controller.state.is_complete:
            self._show_information(
                "Trace complete", "All addresses have been processed."
            )
            return False
        try:
            self._render(self.controller.step())
        except (RuntimeError, StopIteration, ValueError) as exc:
            self._show_error(str(exc))
            return False
        return True

    def run_all_experiment(self) -> bool:
        if not self._ensure_current_session():
            return False
        if self.controller.state.is_complete:
            self._show_information(
                "Trace complete", "All addresses have been processed."
            )
            return False
        try:
            self._render(self.controller.run_all())
        except (RuntimeError, ValueError) as exc:
            self._show_error(str(exc))
            return False
        return True

    def select_timeline_step(self, step_index: int) -> bool:
        try:
            self._render(self.controller.select_step(step_index))
        except RuntimeError as exc:
            self._show_error(str(exc))
            return False
        return True

    def _ensure_current_session(self) -> bool:
        signature = self.controls.input_signature()
        if (
            not self.controller.state.has_session
            or signature != self._session_signature
        ):
            return self._start_from_inputs() is not None
        return True

    def _start_from_inputs(self) -> LocalityPageState | None:
        try:
            addresses = parse_address_trace(
                self.controls.trace_input.toPlainText()
            )
            config = CacheConfig(
                cache_size_bytes=int(
                    self.controls.cache_size_combo.currentData()
                ),
                block_size_bytes=int(
                    self.controls.block_size_combo.currentData()
                ),
                ways=int(self.controls.ways_combo.currentData()),
                replacement_policy=str(
                    self.controls.policy_combo.currentData()
                ),
            )
            state = self.controller.start_session(config, addresses)
        except (TypeError, ValueError) as exc:
            self._show_error(str(exc))
            return None
        self._session_signature = self.controls.input_signature()
        self._render(state)
        return state

    def _render(self, state: LocalityPageState) -> None:
        self.current_panel.render(
            state.current_step, has_session=state.has_session
        )
        self.evidence_panel.render(state.selected_evidence)
        self.cache_panel.render(state.config, state.cache_lines)
        self.block_access_map.render(
            state.block_access_cells, state.block_summaries
        )
        self.statistics_panel.render(state.statistics_view)
        self.timeline.render(state.timeline_items)

    def _update_teaching_card(self) -> None:
        preset = self.controls.current_preset()
        self.preset_title_label.setText(preset.title)
        self.preset_description_label.setText(preset.description)
        self.preset_conclusion_label.setText(
            "Teaching expectation: " + preset.expected_teaching_conclusion
        )
        self.matrix_hint_label.setVisible(
            preset.preset_id in {"matrix_row_major", "matrix_column_major"}
        )

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Invalid Locality experiment", message)

    def _show_information(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)


__all__ = ["LocalityLabWidget"]
