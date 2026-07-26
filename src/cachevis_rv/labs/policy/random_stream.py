"""Isolated seeded replay around the core module-level random source."""

import random
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


class IsolatedRandomStream:
    """Temporarily lend a private RNG state to module-level random."""

    def __init__(self, seed: int) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("random seed must be an integer")
        self.seed = seed
        self.reset()

    @property
    def draw_index(self) -> int:
        return self._draw_count

    def reset(self) -> None:
        self._rng = random.Random(self.seed)
        self._draw_count = 0

    def run(self, operation: Callable[[], T]) -> T:
        """Run exactly one operation while preserving caller global state."""
        if not callable(operation):
            raise TypeError("operation must be callable")
        global_state = random.getstate()
        private_state = self._rng.getstate()
        random.setstate(private_state)
        try:
            return operation()
        finally:
            updated_private_state = random.getstate()
            self._rng.setstate(updated_private_state)
            if updated_private_state != private_state:
                self._draw_count += 1
            random.setstate(global_state)


__all__ = ["IsolatedRandomStream"]
