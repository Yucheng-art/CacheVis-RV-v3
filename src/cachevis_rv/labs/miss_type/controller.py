"""Pure-Python controller for future Miss Type Lab presentation."""

from cachevis_rv.core import CacheConfig

from .cache_view_model import build_cache_line_models
from .evidence_view_model import build_evidence_view_model
from .page_state import EMPTY_PAGE_STATE, MissTypePageState
from .session import MissTypeSession


REFERENCE_DESCRIPTION = (
    "Same capacity and block size as the actual cache; "
    "fully associative (one set) with LRU replacement."
)


class MissTypeController:
    """Coordinate a MissTypeSession and publish immutable page state."""

    def __init__(self) -> None:
        self._session: MissTypeSession | None = None
        self._state = EMPTY_PAGE_STATE

    @property
    def state(self) -> MissTypePageState:
        """Return the most recently published page state."""
        return self._state

    def get_state(self) -> MissTypePageState:
        """Return the current page state for method-oriented callers."""
        return self._state

    def clear_session(self) -> MissTypePageState:
        """Discard the active session and return the canonical empty state."""
        self._session = None
        self._state = EMPTY_PAGE_STATE
        return self._state

    def start_session(
        self,
        config: CacheConfig,
        addresses: list[int],
    ) -> MissTypePageState:
        """Start a validated LRU session without parsing user text."""
        if not isinstance(config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        if not isinstance(addresses, list):
            raise TypeError("addresses must be a list of integers")
        self._session = MissTypeSession(config, addresses)
        return self._publish_initial_state()

    def reset(self) -> MissTypePageState:
        """Reset the active config and trace to their initial cache state."""
        session = self._require_session()
        session.reset()
        return self._publish_initial_state()

    def step(self) -> MissTypePageState:
        """Execute one access and select the new current step."""
        session = self._require_session()
        step = session.step()
        self._state = self._build_state(
            current_step=step,
            selected_step=step,
        )
        return self._state

    def run_all(self) -> MissTypePageState:
        """Execute every remaining access and select the final step."""
        session = self._require_session()
        while session.has_next():
            self.step()
        return self._state

    def select_step(self, step_index: int) -> MissTypePageState:
        """Select historical evidence without rolling back current caches."""
        session = self._require_session()
        selected = next(
            (step for step in session.steps if step.step_index == step_index),
            None,
        )
        if selected is None:
            return self._state
        self._state = MissTypePageState(
            config=self._state.config,
            addresses=self._state.addresses,
            current_step=self._state.current_step,
            selected_step=selected,
            timeline_steps=self._state.timeline_steps,
            actual_cache_lines=self._state.actual_cache_lines,
            reference_cache_lines=self._state.reference_cache_lines,
            statistics=self._state.statistics,
            selected_evidence=build_evidence_view_model(selected),
            has_session=True,
            is_complete=self._state.is_complete,
            next_step_index=self._state.next_step_index,
            reference_config=self._state.reference_config,
            reference_description=self._state.reference_description,
        )
        return self._state

    def _publish_initial_state(self) -> MissTypePageState:
        self._state = self._build_state(
            current_step=None,
            selected_step=None,
        )
        return self._state

    def _build_state(self, *, current_step, selected_step) -> MissTypePageState:
        session = self._require_session()
        return MissTypePageState(
            config=session.actual_config,
            addresses=session.addresses,
            current_step=current_step,
            selected_step=selected_step,
            timeline_steps=session.steps,
            actual_cache_lines=build_cache_line_models(
                session.get_actual_cache_snapshot(),
                "actual",
            ),
            reference_cache_lines=build_cache_line_models(
                session.get_reference_cache_snapshot(),
                "reference",
            ),
            statistics=session.statistics,
            selected_evidence=(
                build_evidence_view_model(selected_step)
                if selected_step is not None
                else None
            ),
            has_session=True,
            is_complete=session.is_complete,
            next_step_index=session.next_step_index,
            reference_config=session.reference_config,
            reference_description=REFERENCE_DESCRIPTION,
        )

    def _require_session(self) -> MissTypeSession:
        if self._session is None:
            raise RuntimeError("no active Miss Type session")
        return self._session


__all__ = ["MissTypeController", "REFERENCE_DESCRIPTION"]
