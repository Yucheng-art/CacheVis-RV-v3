"""Scrollable Miss Type Lab page orchestration."""

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

from ..controller import MissTypeController
from ..page_state import MissTypePageState
from ..statistics_view_model import build_statistics_view_model
from ..timeline_view_model import build_timeline_items
from .cache_panel import CachePanel
from .current_access_panel import CurrentAccessPanel
from .evidence_panel import EvidencePanel
from .experiment_controls import ExperimentControls
from .statistics_panel import StatisticsPanel
from .timeline import MissTypeTimeline


class MissTypeLabWidget(QScrollArea):
    """Complete 3C teaching page backed exclusively by MissTypeController."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MissTypeLabWidget")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.controller = MissTypeController()
        self._session_signature: tuple[str, int, int, int] | None = None
        self._build_ui()
        self._connect_signals()
        self._render(self.controller.state)

    def _build_ui(self) -> None:
        content = QWidget()
        content.setObjectName("MissTypeLabContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 30)
        layout.setSpacing(16)

        title = QLabel("Miss Type Lab")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        subtitle = QLabel(
            "Understand compulsory, conflict, and capacity misses through "
            "an actual cache and a same-capacity fully associative LRU reference."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("role", "muted")
        layout.addWidget(subtitle)

        self.controls = ExperimentControls()
        layout.addWidget(self.controls)
        self.current_panel = CurrentAccessPanel()
        layout.addWidget(self.current_panel)

        cache_grid = QGridLayout()
        self.actual_cache_panel = CachePanel("Actual Cache", "actual")
        self.reference_cache_panel = CachePanel(
            "Fully Associative Reference Cache", "reference"
        )
        cache_grid.addWidget(self.actual_cache_panel, 0, 0)
        cache_grid.addWidget(self.reference_cache_panel, 0, 1)
        cache_grid.setColumnStretch(0, 1)
        cache_grid.setColumnStretch(1, 1)
        layout.addLayout(cache_grid)

        evidence_grid = QGridLayout()
        self.evidence_panel = EvidencePanel()
        self.statistics_panel = StatisticsPanel()
        evidence_grid.addWidget(self.evidence_panel, 0, 0)
        evidence_grid.addWidget(self.statistics_panel, 0, 1)
        evidence_grid.setColumnStretch(0, 1)
        evidence_grid.setColumnStretch(1, 1)
        layout.addLayout(evidence_grid)

        self.timeline = MissTypeTimeline()
        layout.addWidget(self.timeline)
        layout.addStretch(1)
        self.setWidget(content)

    def _connect_signals(self) -> None:
        self.controls.preset_combo.currentIndexChanged.connect(self._preset_changed)
        self.controls.reset_button.clicked.connect(self.reset_experiment)
        self.controls.step_button.clicked.connect(self.step_experiment)
        self.controls.run_all_button.clicked.connect(self.run_all_experiment)
        self.timeline.step_selected.connect(self.select_timeline_step)

    def _preset_changed(self, _index: int) -> None:
        self.controls.apply_preset(self.controls.current_preset())
        self._session_signature = None
        self._render(self.controller.clear_session())

    def reset_experiment(self) -> bool:
        state = self._start_from_inputs()
        return state is not None

    def step_experiment(self) -> bool:
        if not self._ensure_current_session():
            return False
        if self.controller.state.is_complete:
            self._show_information("Trace complete", "All addresses have been processed.")
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
            self._show_information("Trace complete", "All addresses have been processed.")
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

    def _start_from_inputs(self) -> MissTypePageState | None:
        try:
            addresses = parse_address_trace(self.controls.trace_input.toPlainText())
            config = CacheConfig(
                cache_size_bytes=int(self.controls.cache_size_combo.currentData()),
                block_size_bytes=int(self.controls.block_size_combo.currentData()),
                ways=int(self.controls.ways_combo.currentData()),
                replacement_policy="LRU",
            )
            state = self.controller.start_session(config, addresses)
        except (TypeError, ValueError) as exc:
            self._show_error(str(exc))
            return None
        self._session_signature = self.controls.input_signature()
        self._render(state)
        return state

    def _render(self, state: MissTypePageState) -> None:
        self.current_panel.render(state.current_step, has_session=state.has_session)
        self.actual_cache_panel.render(
            state.config,
            state.actual_cache_lines,
            "Real sets and ways",
        )
        self.reference_cache_panel.render(
            state.reference_config,
            state.reference_cache_lines,
            state.reference_description or "Same-capacity fully associative reference",
        )
        self.evidence_panel.render(state.selected_evidence)
        self.statistics_panel.render(build_statistics_view_model(state.statistics))
        current_index = (
            state.current_step.step_index if state.current_step is not None else None
        )
        selected_index = (
            state.selected_step.step_index if state.selected_step is not None else None
        )
        self.timeline.render(
            build_timeline_items(
                state.timeline_steps,
                current_step_index=current_index,
                selected_step_index=selected_index,
            )
        )

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Invalid Miss Type experiment", message)

    def _show_information(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)


__all__ = ["MissTypeLabWidget"]
