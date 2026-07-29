"""Scrollable Write Policy Lab orchestrated exclusively through its controller."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from ..controller import WritePolicyController
from .cache_panel import CachePanel
from .comparison_panel import ComparisonPanel
from .current_access_panel import CurrentAccessPanel
from .decision_panel import DecisionPanel
from .divergence_panel import DivergencePanel
from .experiment_controls import ExperimentControls
from .statistics_panel import StatisticsPanel
from .teaching_summary_panel import TeachingSummaryPanel
from .timeline_panel import TimelinePanel
from .traffic_panel import TrafficPanel


class WritePolicyLabWidget(QScrollArea):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.setObjectName("WritePolicyLabWidget")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.controller = controller if controller is not None else WritePolicyController()
        self._build_ui(); self._connect_signals(); self._render(self.controller.state)

    def _build_ui(self):
        content = QWidget(); content.setObjectName("WritePolicyLabContent")
        content.setStyleSheet(
            "QWidget#WritePolicyLabContent { background: #0b1220; color: #eef4ff; }"
            "QWidget#WritePolicyLabContent QLabel { color: #eef4ff; }"
            "QWidget#WritePolicyLabContent QHeaderView::section { background: #24364d; color: #eef4ff; padding: 5px; }"
        )
        layout = QVBoxLayout(content); layout.setContentsMargins(28, 24, 28, 34); layout.setSpacing(16)
        title = QLabel("Write Policy Lab"); title.setStyleSheet("font-size: 30px; font-weight: 800;"); layout.addWidget(title)
        subtitle = QLabel("Compare write propagation, allocation, dirty state, eviction, and lower-memory traffic across four synchronized cache lanes.")
        subtitle.setWordWrap(True); subtitle.setStyleSheet("color: #b6c5da;"); layout.addWidget(subtitle)
        flow = QLabel("Write Hit: WT propagates immediately; WB marks dirty.  |  Write Miss: WA fills; NWA bypasses.  |  Dirty victims write back a whole block.")
        flow.setWordWrap(True); flow.setStyleSheet("background: #dcecff; color: #163a63; padding: 10px; border: 1px solid #7ea7d2; border-radius: 7px; font-weight: 700;"); layout.addWidget(flow)
        self.controls = ExperimentControls(); self.teaching_panel = TeachingSummaryPanel()
        self.current_access_panel = CurrentAccessPanel(); self.divergence_panel = DivergencePanel()
        self.decision_panel = DecisionPanel(); self.cache_panel = CachePanel(); self.traffic_panel = TrafficPanel()
        self.statistics_panel = StatisticsPanel(); self.timeline_panel = TimelinePanel(); self.comparison_panel = ComparisonPanel()
        for panel in (self.controls, self.teaching_panel, self.current_access_panel, self.divergence_panel,
                      self.decision_panel, self.cache_panel, self.traffic_panel, self.statistics_panel,
                      self.timeline_panel, self.comparison_panel): layout.addWidget(panel)
        layout.addStretch(1); self.setWidget(content)

    def _connect_signals(self):
        self.controls.load_requested.connect(self.load_experiment)
        self.controls.reset_requested.connect(self.reset_experiment)
        self.controls.step_requested.connect(self.step)
        self.controls.run_all_requested.connect(self.run_all)
        self.controls.clear_requested.connect(self.clear)
        self.timeline_panel.step_selected.connect(self.select_step)

    def load_experiment(self):
        try:
            config, accesses, assumptions = self.controls.build_inputs()
            preset = self.controls.current_preset()
            state = self.controller.load_experiment(
                config, accesses, assumptions, experiment_id=preset.preset_id,
                title=preset.title, description=preset.description,
                expected_teaching_conclusion=preset.expected_teaching_conclusion,
            )
        except (TypeError, ValueError) as exc:
            self.controls.set_error(str(exc)); return False
        self.controls.set_error(""); self._render(state); return True

    def reset_experiment(self):
        try: state = self.controller.reset()
        except RuntimeError as exc: self.controls.set_error(str(exc)); return False
        self.controls.set_error(""); self._render(state); return True

    def step(self):
        try: state = self.controller.step()
        except (RuntimeError, StopIteration) as exc: self.controls.set_error(str(exc)); return False
        self.controls.set_error(""); self._render(state); return True

    def run_all(self):
        try: state = self.controller.run_all()
        except RuntimeError as exc: self.controls.set_error(str(exc)); return False
        self.controls.set_error(""); self._render(state); return True

    def select_step(self, step_index):
        try: state = self.controller.select_step(step_index)
        except (RuntimeError, ValueError) as exc: self.controls.set_error(str(exc)); return False
        self.controls.set_error(""); self._render(state); return True

    def select_latest(self):
        try: state = self.controller.select_latest()
        except (RuntimeError, ValueError) as exc: self.controls.set_error(str(exc)); return False
        self.controls.set_error(""); self._render(state); return True

    def clear(self):
        self.controls.set_error(""); self._render(self.controller.clear()); return True

    def _render(self, state):
        self.controls.render_state(state)
        self.teaching_panel.render(state); self.current_access_panel.render(state)
        self.divergence_panel.render(state); self.decision_panel.render(state.selected_lane_decisions)
        self.cache_panel.render(state.current_lane_caches); self.traffic_panel.render(state.current_lane_statistics)
        self.statistics_panel.render(state.current_lane_statistics); self.timeline_panel.render(state.timeline_steps)
        self.comparison_panel.render(state.comparison_summary)


__all__ = ["WritePolicyLabWidget"]
