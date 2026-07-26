"""Immutable complete page state for the future Policy Lab widget."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .cache_view_model import PolicyLaneCacheViewModel
from .decision_view_model import PolicyComparisonEvidenceViewModel
from .divergence_view_model import (
    PolicyDivergenceSummaryViewModel,
    build_divergence_summary,
)
from .model import (
    PolicyComparisonStatistics,
    PolicyComparisonStep,
)
from .statistics_view_model import (
    PolicyComparisonStatisticsViewModel,
    build_statistics_view_model,
)
from .timeline_view_model import PolicyTimelineItemViewModel


@dataclass(frozen=True)
class PolicyPageState:
    config: CacheConfig | None
    addresses: tuple[int, ...]
    random_seed: int | None
    policies: tuple[str, ...]
    current_step: PolicyComparisonStep | None
    selected_step: PolicyComparisonStep | None
    timeline_steps: tuple[PolicyComparisonStep, ...]
    timeline_items: tuple[PolicyTimelineItemViewModel, ...]
    lane_caches: tuple[PolicyLaneCacheViewModel, ...]
    selected_evidence: PolicyComparisonEvidenceViewModel | None
    statistics: PolicyComparisonStatistics
    statistics_view: PolicyComparisonStatisticsViewModel
    divergence_summary: PolicyDivergenceSummaryViewModel
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
        if self.has_session:
            if self.config is None or self.random_seed is None:
                raise ValueError("active state must retain config and random seed")
            if len(self.policies) != 3 or len(self.lane_caches) != 3:
                raise ValueError("active state must contain all three policy lanes")
        elif (
            self.config is not None
            or self.addresses
            or self.random_seed is not None
            or self.policies
            or self.timeline_steps
            or self.timeline_items
            or self.lane_caches
            or self.next_step_index is not None
        ):
            raise ValueError("empty state must not retain session data")


_EMPTY_STATISTICS = PolicyComparisonStatistics()
EMPTY_PAGE_STATE = PolicyPageState(
    config=None,
    addresses=(),
    random_seed=None,
    policies=(),
    current_step=None,
    selected_step=None,
    timeline_steps=(),
    timeline_items=(),
    lane_caches=(),
    selected_evidence=None,
    statistics=_EMPTY_STATISTICS,
    statistics_view=build_statistics_view_model(_EMPTY_STATISTICS),
    divergence_summary=build_divergence_summary(()),
    has_session=False,
    is_complete=False,
    next_step_index=None,
)


__all__ = ["EMPTY_PAGE_STATE", "PolicyPageState"]
