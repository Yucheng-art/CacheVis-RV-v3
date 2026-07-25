"""Immutable page state for the Address Explorer lab."""

from dataclasses import dataclass

from .model import AccessStepViewModel, CacheLineViewModel


CacheLines = tuple[tuple[CacheLineViewModel, ...], ...]


@dataclass(frozen=True)
class AddressExplorerPageState:
    """Complete non-Qt state needed to render the Address Explorer page."""

    current_step: AccessStepViewModel | None
    selected_step: AccessStepViewModel | None
    timeline_steps: tuple[AccessStepViewModel, ...]
    cache_lines: CacheLines
    is_complete: bool
    has_session: bool
    next_step_index: int | None


EMPTY_PAGE_STATE = AddressExplorerPageState(
    current_step=None,
    selected_step=None,
    timeline_steps=(),
    cache_lines=(),
    is_complete=False,
    has_session=False,
    next_step_index=None,
)


def freeze_cache_lines(
    cache_lines: list[list[CacheLineViewModel]],
) -> CacheLines:
    """Freeze nested cache-line lists for safe publication in page state."""
    return tuple(tuple(cache_set) for cache_set in cache_lines)


__all__ = [
    "AddressExplorerPageState",
    "CacheLines",
    "EMPTY_PAGE_STATE",
]
