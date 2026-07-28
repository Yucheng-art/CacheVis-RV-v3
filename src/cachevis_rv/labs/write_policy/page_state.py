"""Immutable aggregate page state for the future Write Policy Lab UI."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .cache_view_model import WritePolicyLaneCacheViewModel
from .comparison_view_model import (
    WritePolicyComparisonSummaryViewModel,
    WritePolicyDivergenceSummaryViewModel,
)
from .decision_view_model import WritePolicyLaneDecisionViewModel
from .model import (
    MemoryAccess,
    WritePolicyComparisonStatistics,
    WritePolicyComparisonStep,
    WritePolicyLaneSpec,
    WriteTrafficAssumptions,
)
from .statistics_view_model import WritePolicyLaneStatisticsViewModel
from .timeline_view_model import WritePolicyTimelineStepViewModel


@dataclass(frozen=True)
class WritePolicyPageState:
    experiment_id: str | None
    title: str | None
    description: str | None
    expected_teaching_conclusion: str | None
    config: CacheConfig | None
    accesses: tuple[MemoryAccess, ...]
    assumptions: WriteTrafficAssumptions | None
    lanes: tuple[WritePolicyLaneSpec, ...]
    has_experiment: bool
    total_steps: int
    next_step_index: int
    is_complete: bool
    latest_step_index: int | None
    selected_step_index: int | None
    selected_is_latest: bool
    latest_step: WritePolicyComparisonStep | None
    selected_step: WritePolicyComparisonStep | None
    selected_lane_decisions: tuple[WritePolicyLaneDecisionViewModel, ...]
    current_lane_caches: tuple[WritePolicyLaneCacheViewModel, ...]
    current_lane_statistics: tuple[WritePolicyLaneStatisticsViewModel, ...]
    current_comparison_statistics: WritePolicyComparisonStatistics | None
    divergence_summary: WritePolicyDivergenceSummaryViewModel | None
    comparison_summary: WritePolicyComparisonSummaryViewModel | None
    timeline_steps: tuple[WritePolicyTimelineStepViewModel, ...]

    def __post_init__(self) -> None:
        for name in (
            "accesses", "lanes", "selected_lane_decisions", "current_lane_caches",
            "current_lane_statistics", "timeline_steps",
        ):
            if not isinstance(getattr(self, name), tuple):
                raise TypeError(f"{name} must be a tuple")
        if self.has_experiment != (self.config is not None):
            raise ValueError("has_experiment is inconsistent with config")
        if self.latest_step_index != (
            None if self.latest_step is None else self.latest_step.step_index
        ):
            raise ValueError("latest step fields are inconsistent")
        if self.selected_step_index != (
            None if self.selected_step is None else self.selected_step.step_index
        ):
            raise ValueError("selected step fields are inconsistent")
        if self.selected_is_latest != (
            self.selected_step_index is not None
            and self.selected_step_index == self.latest_step_index
        ):
            raise ValueError("selected_is_latest is inconsistent")


def empty_write_policy_page_state() -> WritePolicyPageState:
    return WritePolicyPageState(
        experiment_id=None,
        title=None,
        description=None,
        expected_teaching_conclusion=None,
        config=None,
        accesses=(),
        assumptions=None,
        lanes=(),
        has_experiment=False,
        total_steps=0,
        next_step_index=0,
        is_complete=False,
        latest_step_index=None,
        selected_step_index=None,
        selected_is_latest=False,
        latest_step=None,
        selected_step=None,
        selected_lane_decisions=(),
        current_lane_caches=(),
        current_lane_statistics=(),
        current_comparison_statistics=None,
        divergence_summary=None,
        comparison_summary=None,
        timeline_steps=(),
    )


EMPTY_WRITE_POLICY_PAGE_STATE = empty_write_policy_page_state()


__all__ = [
    "EMPTY_WRITE_POLICY_PAGE_STATE",
    "WritePolicyPageState",
    "empty_write_policy_page_state",
]
