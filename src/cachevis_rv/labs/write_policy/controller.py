"""Pure controller for incremental write-policy experiments."""

from dataclasses import replace

from cachevis_rv.core import CacheConfig

from .cache_view_model import build_lane_cache_view_model
from .comparison_view_model import (
    build_comparison_summary_view_model,
    build_divergence_summary_view_model,
)
from .decision_view_model import build_lane_decision_view_model
from .model import MemoryAccess, WritePolicyPreset, WriteTrafficAssumptions
from .page_state import WritePolicyPageState, empty_write_policy_page_state
from .session import WritePolicyComparisonSession
from .statistics_view_model import build_lane_statistics_view_model
from .timeline_view_model import build_timeline_view_models


class WritePolicyController:
    def __init__(self, session_factory=WritePolicyComparisonSession) -> None:
        self._session_factory = session_factory
        self._session = None
        self._definition = None
        self._steps = ()
        self._selected_step_index = None
        self._state = empty_write_policy_page_state()

    @property
    def state(self) -> WritePolicyPageState:
        return self._state

    def get_state(self) -> WritePolicyPageState:
        return self._state

    def load_experiment(
        self,
        config: CacheConfig,
        accesses: tuple[MemoryAccess, ...],
        assumptions: WriteTrafficAssumptions,
        experiment_id=None,
        title=None,
        description=None,
        expected_teaching_conclusion=None,
    ) -> WritePolicyPageState:
        immutable_accesses = tuple(accesses)
        session = self._session_factory(config, immutable_accesses, assumptions)
        self._session = session
        self._steps = ()
        self._definition = (
            experiment_id,
            title,
            description,
            expected_teaching_conclusion,
            config,
            immutable_accesses,
            assumptions,
        )
        self._selected_step_index = None
        return self._publish_state()

    def load_preset(self, preset: WritePolicyPreset) -> WritePolicyPageState:
        if not isinstance(preset, WritePolicyPreset):
            raise ValueError("preset must be a WritePolicyPreset")
        return self.load_experiment(
            preset.config,
            preset.accesses,
            preset.assumptions,
            experiment_id=preset.preset_id,
            title=preset.title,
            description=preset.description,
            expected_teaching_conclusion=preset.expected_teaching_conclusion,
        )

    def reset(self) -> WritePolicyPageState:
        session = self._require_session()
        session.reset()
        self._steps = ()
        self._selected_step_index = None
        return self._publish_state()

    def has_next(self) -> bool:
        return False if self._session is None else self._session.has_next()

    def step(self) -> WritePolicyPageState:
        session = self._require_session()
        completed_step = session.step()
        self._steps = session.steps
        self._selected_step_index = completed_step.step_index
        return self._publish_state()

    def run_all(self) -> WritePolicyPageState:
        session = self._require_session()
        session.run_all()
        self._steps = session.steps
        if self._steps:
            self._selected_step_index = self._steps[-1].step_index
        return self._publish_state()

    def select_step(self, step_index: int) -> WritePolicyPageState:
        session = self._require_session()
        if isinstance(step_index, bool) or not isinstance(step_index, int):
            raise ValueError("step_index must identify a completed step")
        if not any(step.step_index == step_index for step in self._steps):
            raise ValueError("step_index must identify a completed step")
        self._selected_step_index = step_index
        return self._publish_selection_state()

    def select_latest(self) -> WritePolicyPageState:
        session = self._require_session()
        if not self._steps:
            raise ValueError("there is no completed step to select")
        self._selected_step_index = self._steps[-1].step_index
        return self._publish_selection_state()

    def clear(self) -> WritePolicyPageState:
        self._session = None
        self._definition = None
        self._steps = ()
        self._selected_step_index = None
        self._state = empty_write_policy_page_state()
        return self._state

    def _require_session(self):
        if self._session is None:
            raise RuntimeError("no write-policy experiment is loaded")
        return self._session

    def _publish_state(self) -> WritePolicyPageState:
        session = self._require_session()
        (
            experiment_id,
            title,
            description,
            conclusion,
            config,
            accesses,
            assumptions,
        ) = self._definition
        steps = session.steps
        self._steps = steps
        latest_step = steps[-1] if steps else None
        selected_step = next(
            (step for step in steps if step.step_index == self._selected_step_index), None
        )
        statistics = session.statistics
        snapshots = dict(session.get_all_cache_snapshots())
        caches = tuple(
            build_lane_cache_view_model(
                lane, snapshots[lane.lane_id], config.block_size_bytes
            )
            for lane in session.lanes
        )
        lane_statistics = tuple(
            build_lane_statistics_view_model(item)
            for item in statistics.lane_statistics
        )
        decisions = (
            tuple(
                build_lane_decision_view_model(lane_step.evidence)
                for lane_step in selected_step.lane_steps
            )
            if selected_step is not None
            else ()
        )
        latest_index = latest_step.step_index if latest_step is not None else None
        self._state = WritePolicyPageState(
            experiment_id=experiment_id,
            title=title,
            description=description,
            expected_teaching_conclusion=conclusion,
            config=config,
            accesses=accesses,
            assumptions=assumptions,
            lanes=tuple(session.lanes),
            has_experiment=True,
            total_steps=len(accesses),
            next_step_index=session.next_step_index,
            is_complete=session.is_complete,
            latest_step_index=latest_index,
            selected_step_index=self._selected_step_index,
            selected_is_latest=(
                self._selected_step_index is not None
                and self._selected_step_index == latest_index
            ),
            latest_step=latest_step,
            selected_step=selected_step,
            selected_lane_decisions=decisions,
            current_lane_caches=caches,
            current_lane_statistics=lane_statistics,
            current_comparison_statistics=statistics,
            divergence_summary=build_divergence_summary_view_model(statistics, steps),
            comparison_summary=build_comparison_summary_view_model(statistics, steps),
            timeline_steps=build_timeline_view_models(steps, self._selected_step_index),
        )
        return self._state

    def _publish_selection_state(self) -> WritePolicyPageState:
        selected_step = next(
            step for step in self._steps if step.step_index == self._selected_step_index
        )
        latest_index = self._steps[-1].step_index
        self._state = replace(
            self._state,
            selected_step_index=self._selected_step_index,
            selected_is_latest=self._selected_step_index == latest_index,
            selected_step=selected_step,
            selected_lane_decisions=tuple(
                build_lane_decision_view_model(lane_step.evidence)
                for lane_step in selected_step.lane_steps
            ),
            timeline_steps=build_timeline_view_models(
                self._steps, self._selected_step_index
            ),
        )
        return self._state


__all__ = ["WritePolicyController"]
