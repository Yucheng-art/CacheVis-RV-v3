"""Pure-Python session controller for the Address Explorer lab."""

from cachevis_rv.core import CacheConfig

from .engine import VisualizerStepEngine
from .page_state import (
    EMPTY_PAGE_STATE,
    AddressExplorerPageState,
    freeze_cache_lines,
)


class AddressExplorerController:
    """Own one visualizer session and publish immutable page state."""

    def __init__(self) -> None:
        self._engine: VisualizerStepEngine | None = None
        self._state = EMPTY_PAGE_STATE

    @property
    def state(self) -> AddressExplorerPageState:
        """Return the current page state."""
        return self._state

    def get_state(self) -> AddressExplorerPageState:
        """Return the current page state for callers preferring a method API."""
        return self._state

    def clear_session(self) -> AddressExplorerPageState:
        """Discard the current session and return the empty page state."""
        self._engine = None
        self._state = EMPTY_PAGE_STATE
        return self._state

    def start_session(
        self,
        config: CacheConfig,
        addresses: list[int],
    ) -> AddressExplorerPageState:
        """Start a fresh validated trace and return its initial cache state."""
        self._engine = VisualizerStepEngine(config, addresses)
        return self._publish_initial_state()

    def reset(self) -> AddressExplorerPageState:
        """Reset the active trace to its initial cache and timeline state."""
        engine = self._require_engine()
        engine.reset()
        return self._publish_initial_state()

    def step(self) -> AddressExplorerPageState:
        """Execute one address and select the newly current step."""
        engine = self._require_engine()
        step = engine.step()
        timeline_steps = (*self._state.timeline_steps, step)
        self._state = AddressExplorerPageState(
            current_step=step,
            selected_step=step,
            timeline_steps=timeline_steps,
            cache_lines=freeze_cache_lines(engine.get_cache_line_models()),
            is_complete=engine.is_complete,
            has_session=True,
            next_step_index=engine.next_step_index,
        )
        return self._state

    def run_all(self) -> AddressExplorerPageState:
        """Execute all remaining addresses and select the final step."""
        engine = self._require_engine()
        while engine.has_next():
            self.step()
        return self._state

    def select_step(self, step_index: int) -> AddressExplorerPageState:
        """Select a historical summary without changing current cache state."""
        selected = next(
            (
                step
                for step in self._state.timeline_steps
                if step.step_index == step_index
            ),
            None,
        )
        if selected is None:
            return self._state
        self._state = AddressExplorerPageState(
            current_step=self._state.current_step,
            selected_step=selected,
            timeline_steps=self._state.timeline_steps,
            cache_lines=self._state.cache_lines,
            is_complete=self._state.is_complete,
            has_session=self._state.has_session,
            next_step_index=self._state.next_step_index,
        )
        return self._state

    def _publish_initial_state(self) -> AddressExplorerPageState:
        engine = self._require_engine()
        self._state = AddressExplorerPageState(
            current_step=None,
            selected_step=None,
            timeline_steps=(),
            cache_lines=freeze_cache_lines(engine.get_cache_line_models()),
            is_complete=engine.is_complete,
            has_session=True,
            next_step_index=engine.next_step_index,
        )
        return self._state

    def _require_engine(self) -> VisualizerStepEngine:
        if self._engine is None:
            raise RuntimeError("no active Address Explorer session")
        return self._engine


__all__ = ["AddressExplorerController"]
