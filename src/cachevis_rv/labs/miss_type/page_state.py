"""Immutable complete page state for a future Miss Type Lab widget."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .cache_view_model import MissTypeCacheLineViewModel
from .evidence_view_model import MissTypeEvidenceViewModel
from .model import MissTypeStatistics, MissTypeStep


@dataclass(frozen=True)
class MissTypePageState:
    """All pure state required to render and navigate one Miss Type session."""

    config: CacheConfig | None
    addresses: tuple[int, ...]
    current_step: MissTypeStep | None
    selected_step: MissTypeStep | None
    timeline_steps: tuple[MissTypeStep, ...]
    actual_cache_lines: tuple[MissTypeCacheLineViewModel, ...]
    reference_cache_lines: tuple[MissTypeCacheLineViewModel, ...]
    statistics: MissTypeStatistics
    selected_evidence: MissTypeEvidenceViewModel | None
    has_session: bool
    is_complete: bool
    next_step_index: int | None
    reference_config: CacheConfig | None
    reference_description: str | None

    def __post_init__(self) -> None:
        if self.selected_step is None and self.selected_evidence is not None:
            raise ValueError("selected_evidence requires a selected_step")
        if self.selected_step is not None and self.selected_evidence is None:
            raise ValueError("selected_step requires selected_evidence")
        if self.current_step is not None:
            if not self.timeline_steps or self.current_step != self.timeline_steps[-1]:
                raise ValueError("current_step must be the latest timeline step")
        if not self.has_session:
            if self.config is not None or self.reference_config is not None:
                raise ValueError("empty page state must not retain cache configuration")
            if self.next_step_index is not None:
                raise ValueError("empty page state must not have a next step index")


EMPTY_PAGE_STATE = MissTypePageState(
    config=None,
    addresses=(),
    current_step=None,
    selected_step=None,
    timeline_steps=(),
    actual_cache_lines=(),
    reference_cache_lines=(),
    statistics=MissTypeStatistics(),
    selected_evidence=None,
    has_session=False,
    is_complete=False,
    next_step_index=None,
    reference_config=None,
    reference_description=None,
)


__all__ = ["EMPTY_PAGE_STATE", "MissTypePageState"]
