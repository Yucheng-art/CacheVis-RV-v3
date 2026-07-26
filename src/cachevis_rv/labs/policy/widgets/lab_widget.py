"""Scrollable Policy Lab page orchestration."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QLabel, QMessageBox, QScrollArea, QVBoxLayout, QWidget,
)

from cachevis_rv.core import CacheConfig
from cachevis_rv.experiments.address_trace_parser import parse_address_trace

from ..controller import PolicyController
from ..page_state import PolicyPageState
from .cache_panel import CachePanel
from .current_access_panel import CurrentAccessPanel
from .decision_panel import DecisionPanel
from .divergence_panel import DivergencePanel
from .experiment_controls import ExperimentControls
from .statistics_panel import StatisticsPanel
from .timeline import PolicyTimeline


class PolicyLabWidget(QScrollArea):
    """Complete GUI backed exclusively by PolicyController and view models."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("PolicyLabWidget")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.controller = PolicyController()
        self._session_signature: tuple[str, int, int, int, str] | None = None
        self._build_ui()
        self._connect_signals()
        self._update_teaching_card()
        self._render(self.controller.state)

    def _build_ui(self) -> None:
        content = QWidget()
        content.setObjectName("PolicyLabContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 30)
        layout.setSpacing(16)
        title = QLabel("Policy Lab")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        layout.addWidget(title)
        subtitle = QLabel(
            "Compare LRU, FIFO, and seeded Random on the same address trace: "
            "decision evidence → victim choice → cache state → future outcomes."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("role", "muted")
        layout.addWidget(subtitle)
        causal = QLabel(
            "Same address → Same set and tag → Each policy inspects its own state → "
            "HIT / INVALID FILL / EVICTION → Victim decision → Cache state divergence "
            "→ Possible future HIT/MISS divergence"
        )
        causal.setObjectName("PolicyCausalChain")
        causal.setWordWrap(True)
        causal.setStyleSheet(
            "background: #e8eef6; color: #20364d; border: 1px solid #8ba2ba;"
            "border-radius: 7px; padding: 10px; font-weight: 700;"
        )
        layout.addWidget(causal)
        self.controls = ExperimentControls()
        layout.addWidget(self.controls)
        self.teaching_panel = self._build_teaching_panel()
        layout.addWidget(self.teaching_panel)
        self.current_panel = CurrentAccessPanel()
        layout.addWidget(self.current_panel)
        self.divergence_panel = DivergencePanel()
        layout.addWidget(self.divergence_panel)
        self.decision_panel = DecisionPanel()
        layout.addWidget(self.decision_panel)
        self.cache_panel = CachePanel()
        layout.addWidget(self.cache_panel)
        self.statistics_panel = StatisticsPanel()
        layout.addWidget(self.statistics_panel)
        self.timeline = PolicyTimeline()
        layout.addWidget(self.timeline)
        layout.addStretch(1)
        self.setWidget(content)

    def _build_teaching_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("PolicyTeachingPanel")
        panel.setStyleSheet(
            "QFrame#PolicyTeachingPanel { background: #f7f2ff;"
            " border: 1px solid #a78bca; border-radius: 8px; }"
            "QFrame#PolicyTeachingPanel QLabel { color: #3f2768; }"
        )
        layout = QVBoxLayout(panel)
        heading = QLabel("Preset Teaching Insight")
        heading.setStyleSheet("font-size: 17px; font-weight: 750;")
        layout.addWidget(heading)
        self.preset_title_label = QLabel()
        self.preset_title_label.setStyleSheet("font-weight: 850;")
        layout.addWidget(self.preset_title_label)
        self.preset_description_label = QLabel()
        self.preset_description_label.setWordWrap(True)
        layout.addWidget(self.preset_description_label)
        self.preset_conclusion_label = QLabel()
        self.preset_conclusion_label.setWordWrap(True)
        layout.addWidget(self.preset_conclusion_label)
        return panel

    def _connect_signals(self) -> None:
        self.controls.preset_combo.currentIndexChanged.connect(self._preset_changed)
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
        if not self.controller.state.has_session or signature != self._session_signature:
            return self._start_from_inputs() is not None
        return True

    def _start_from_inputs(self) -> PolicyPageState | None:
        try:
            addresses = parse_address_trace(self.controls.trace_input.toPlainText())
            seed_text = self.controls.seed_input.text().strip()
            if not seed_text:
                raise ValueError("random seed is required")
            try:
                random_seed = int(seed_text)
            except ValueError as exc:
                raise ValueError("random seed must be an integer") from exc
            config = CacheConfig(
                cache_size_bytes=int(self.controls.cache_size_combo.currentData()),
                block_size_bytes=int(self.controls.block_size_combo.currentData()),
                ways=int(self.controls.ways_combo.currentData()),
                replacement_policy="LRU",
            )
            state = self.controller.start_session(
                config, addresses, random_seed=random_seed
            )
        except (TypeError, ValueError) as exc:
            self._show_error(str(exc))
            return None
        self._session_signature = self.controls.input_signature()
        self._render(state)
        return state

    def _render(self, state: PolicyPageState) -> None:
        self.current_panel.render(state.current_step, has_session=state.has_session)
        self.divergence_panel.render(state.divergence_summary)
        self.decision_panel.render(state.selected_evidence)
        self.cache_panel.render(state.lane_caches)
        self.statistics_panel.render(state.statistics_view)
        self.timeline.render(state.timeline_items)

    def _update_teaching_card(self) -> None:
        preset = self.controls.current_preset()
        self.preset_title_label.setText(preset.title)
        self.preset_description_label.setText(preset.description)
        self.preset_conclusion_label.setText(
            "Teaching expectation: " + preset.expected_teaching_conclusion
        )

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Invalid Policy experiment", message)

    def _show_information(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)


__all__ = ["PolicyLabWidget"]
