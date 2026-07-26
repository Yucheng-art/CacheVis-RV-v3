"""Pure-Python controller for Policy Lab presentation state."""

from collections.abc import Iterable

from cachevis_rv.core import CacheConfig

from .cache_view_model import build_lane_cache_view_models
from .decision_view_model import build_comparison_evidence_view_model
from .divergence_view_model import build_divergence_summary
from .model import PolicyComparisonStep
from .page_state import EMPTY_PAGE_STATE, PolicyPageState
from .session import PolicyComparisonSession
from .statistics_view_model import build_statistics_view_model
from .timeline_view_model import build_timeline_items


class PolicyController:
    """Coordinate a comparison session and publish immutable page state."""

    def __init__(self) -> None:
        self._session: PolicyComparisonSession | None = None
        self._state = EMPTY_PAGE_STATE

    @property
    def state(self) -> PolicyPageState:
        return self._state

    def get_state(self) -> PolicyPageState:
        return self._state

    def clear_session(self) -> PolicyPageState:
        self._session = None
        self._state = EMPTY_PAGE_STATE
        return self._state

    def start_session(
        self,
        config: CacheConfig,
        addresses: Iterable[int],
        random_seed: int = 2026,
    ) -> PolicyPageState:
        self._session = PolicyComparisonSession(
            config,
            addresses,
            random_seed=random_seed,
        )
        return self._publish_initial_state()

    def reset(self) -> PolicyPageState:
        self._require_session().reset()
        return self._publish_initial_state()

    def step(self) -> PolicyPageState:
        step = self._require_session().step()
        self._state = self._build_state(
            current_step=step,
            selected_step=step,
        )
        return self._state

    def run_all(self) -> PolicyPageState:
        session = self._require_session()
        while session.has_next():
            self.step()
        return self._state

    def select_step(self, step_index: int) -> PolicyPageState:
        session = self._require_session()
        selected = next(
            (step for step in session.steps if step.step_index == step_index),
            None,
        )
        if selected is None:
            return self._state
        current = self._state.current_step
        self._state = self._build_state(
            current_step=current,
            selected_step=selected,
        )
        return self._state

    def _publish_initial_state(self) -> PolicyPageState:
        self._state = self._build_state(
            current_step=None,
            selected_step=None,
        )
        return self._state

    def _build_state(
        self,
        *,
        current_step: PolicyComparisonStep | None,
        selected_step: PolicyComparisonStep | None,
    ) -> PolicyPageState:
        session = self._require_session()
        current_index = (
            current_step.step_index if current_step is not None else None
        )
        selected_index = (
            selected_step.step_index if selected_step is not None else None
        )
        return PolicyPageState(
            config=session.config,
            addresses=session.addresses,
            random_seed=session.random_seed,
            policies=session.policies,
            current_step=current_step,
            selected_step=selected_step,
            timeline_steps=session.steps,
            timeline_items=build_timeline_items(
                session.steps,
                current_step_index=current_index,
                selected_step_index=selected_index,
            ),
            lane_caches=build_lane_cache_view_models(session, current_step),
            selected_evidence=(
                build_comparison_evidence_view_model(selected_step)
                if selected_step is not None
                else None
            ),
            statistics=session.statistics,
            statistics_view=build_statistics_view_model(session.statistics),
            divergence_summary=build_divergence_summary(session.steps),
            has_session=True,
            is_complete=session.is_complete,
            next_step_index=session.next_step_index,
        )

    def _require_session(self) -> PolicyComparisonSession:
        if self._session is None:
            raise RuntimeError("no active Policy comparison session")
        return self._session


__all__ = ["PolicyController"]
