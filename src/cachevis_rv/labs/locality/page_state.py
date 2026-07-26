"""Immutable complete page state for a future Locality Lab widget."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .block_access_view_model import (
    BlockAccessCellViewModel,
    BlockAccessSummaryViewModel,
)
from .cache_view_model import LocalityCacheLineViewModel
from .evidence_view_model import LocalityEvidenceViewModel
from .model import LocalityStatistics, LocalityStep
from .statistics_view_model import (
    LocalityStatisticsViewModel,
    build_statistics_view_model,
)
from .timeline_view_model import LocalityTimelineItemViewModel


@dataclass(frozen=True)
class LocalityPageState:
    config: CacheConfig | None
    addresses: tuple[int, ...]
    current_step: LocalityStep | None
    selected_step: LocalityStep | None
    timeline_steps: tuple[LocalityStep, ...]
    timeline_items: tuple[LocalityTimelineItemViewModel, ...]
    cache_lines: tuple[LocalityCacheLineViewModel, ...]
    selected_evidence: LocalityEvidenceViewModel | None
    statistics: LocalityStatistics
    statistics_view: LocalityStatisticsViewModel
    block_access_cells: tuple[BlockAccessCellViewModel, ...]
    block_summaries: tuple[BlockAccessSummaryViewModel, ...]
    has_session: bool
    is_complete: bool
    next_step_index: int | None

    def __post_init__(self) -> None:
        if (self.selected_step is None) != (self.selected_evidence is None):
            raise ValueError("selected_step and selected_evidence must be paired")
        if self.current_step is not None and (
            not self.timeline_steps
            or self.current_step != self.timeline_steps[-1]
        ):
            raise ValueError("current_step must be the latest timeline step")
        if len(self.timeline_items) != len(self.timeline_steps):
            raise ValueError("timeline items must match completed steps")
        if not self.has_session:
            if self.config is not None or self.next_step_index is not None:
                raise ValueError("empty state must not retain session values")
            if (
                self.addresses
                or self.timeline_steps
                or self.cache_lines
                or self.block_access_cells
                or self.block_summaries
            ):
                raise ValueError("empty state must not retain session collections")


_EMPTY_STATISTICS = LocalityStatistics()
EMPTY_PAGE_STATE = LocalityPageState(
    config=None,
    addresses=(),
    current_step=None,
    selected_step=None,
    timeline_steps=(),
    timeline_items=(),
    cache_lines=(),
    selected_evidence=None,
    statistics=_EMPTY_STATISTICS,
    statistics_view=build_statistics_view_model(_EMPTY_STATISTICS),
    block_access_cells=(),
    block_summaries=(),
    has_session=False,
    is_complete=False,
    next_step_index=None,
)


__all__ = ["EMPTY_PAGE_STATE", "LocalityPageState"]
