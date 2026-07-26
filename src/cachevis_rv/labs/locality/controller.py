"""Pure-Python controller for Locality Lab presentation state."""

from cachevis_rv.core import CacheConfig

from .block_access_view_model import build_block_access_models
from .cache_view_model import build_cache_line_models
from .evidence_view_model import build_evidence_view_model
from .page_state import EMPTY_PAGE_STATE, LocalityPageState
from .session import LocalitySession
from .statistics_view_model import build_statistics_view_model
from .timeline_view_model import build_timeline_items


class LocalityController:
    """Coordinate a LocalitySession and publish immutable page state."""

    def __init__(self) -> None:
        self._session: LocalitySession | None = None
        self._state = EMPTY_PAGE_STATE

    @property
    def state(self) -> LocalityPageState:
        return self._state

    def get_state(self) -> LocalityPageState:
        return self._state

    def clear_session(self) -> LocalityPageState:
        self._session = None
        self._state = EMPTY_PAGE_STATE
        return self._state

    def start_session(
        self,
        config: CacheConfig,
        addresses: list[int],
    ) -> LocalityPageState:
        if not isinstance(config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        if not isinstance(addresses, list):
            raise TypeError("addresses must be a list of integers")
        self._session = LocalitySession(config, addresses)
        return self._publish_initial_state()

    def reset(self) -> LocalityPageState:
        self._require_session().reset()
        return self._publish_initial_state()

    def step(self) -> LocalityPageState:
        step = self._require_session().step()
        self._state = self._build_state(
            current_step=step,
            selected_step=step,
        )
        return self._state

    def run_all(self) -> LocalityPageState:
        session = self._require_session()
        while session.has_next():
            self.step()
        return self._state

    def select_step(self, step_index: int) -> LocalityPageState:
        session = self._require_session()
        selected = next(
            (step for step in session.steps if step.step_index == step_index),
            None,
        )
        if selected is None:
            return self._state
        current_index = (
            self._state.current_step.step_index
            if self._state.current_step is not None
            else None
        )
        self._state = LocalityPageState(
            config=self._state.config,
            addresses=self._state.addresses,
            current_step=self._state.current_step,
            selected_step=selected,
            timeline_steps=self._state.timeline_steps,
            timeline_items=build_timeline_items(
                self._state.timeline_steps,
                current_step_index=current_index,
                selected_step_index=selected.step_index,
            ),
            cache_lines=self._state.cache_lines,
            selected_evidence=build_evidence_view_model(selected),
            statistics=self._state.statistics,
            statistics_view=self._state.statistics_view,
            block_access_cells=self._state.block_access_cells,
            block_summaries=self._state.block_summaries,
            has_session=True,
            is_complete=self._state.is_complete,
            next_step_index=self._state.next_step_index,
        )
        return self._state

    def _publish_initial_state(self) -> LocalityPageState:
        self._state = self._build_state(
            current_step=None,
            selected_step=None,
        )
        return self._state

    def _build_state(
        self,
        *,
        current_step,
        selected_step,
    ) -> LocalityPageState:
        session = self._require_session()
        current_index = (
            current_step.step_index if current_step is not None else None
        )
        selected_index = (
            selected_step.step_index if selected_step is not None else None
        )
        cells, summaries = build_block_access_models(
            session.steps,
            current_step,
        )
        return LocalityPageState(
            config=session.config,
            addresses=session.addresses,
            current_step=current_step,
            selected_step=selected_step,
            timeline_steps=session.steps,
            timeline_items=build_timeline_items(
                session.steps,
                current_step_index=current_index,
                selected_step_index=selected_index,
            ),
            cache_lines=build_cache_line_models(
                session.get_cache_snapshot(),
                current_step,
            ),
            selected_evidence=(
                build_evidence_view_model(selected_step)
                if selected_step is not None
                else None
            ),
            statistics=session.statistics,
            statistics_view=build_statistics_view_model(session.statistics),
            block_access_cells=cells,
            block_summaries=summaries,
            has_session=True,
            is_complete=session.is_complete,
            next_step_index=session.next_step_index,
        )

    def _require_session(self) -> LocalitySession:
        if self._session is None:
            raise RuntimeError("no active Locality session")
        return self._session


__all__ = ["LocalityController"]
