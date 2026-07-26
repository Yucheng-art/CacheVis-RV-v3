"""Immutable complete state for the future Performance Lab page."""

from dataclasses import dataclass

from .chart_view_model import PerformanceChartMetric, PerformanceChartSeriesViewModel
from .comparison_view_model import PerformanceComparisonViewModel
from .hierarchy import TwoLevelPerformanceResult, TwoLevelTimingModel
from .hierarchy_view_model import TwoLevelPerformanceViewModel
from .sweep import PerformanceSweepDefinition, PerformanceSweepResult
from .sweep_view_model import (
    PerformanceSweepPointViewModel,
    PerformanceSweepSummaryViewModel,
)


@dataclass(frozen=True)
class PerformancePageState:
    sweep_definition: PerformanceSweepDefinition | None
    sweep_result: PerformanceSweepResult | None
    selected_point_id: str | None
    selected_point: PerformanceSweepPointViewModel | None
    point_view_models: tuple[PerformanceSweepPointViewModel, ...]
    chart_metric: PerformanceChartMetric | None
    chart_series: PerformanceChartSeriesViewModel | None
    sweep_summary: PerformanceSweepSummaryViewModel | None
    comparison_view: PerformanceComparisonViewModel | None
    hierarchy_model: TwoLevelTimingModel | None
    hierarchy_result: TwoLevelPerformanceResult | None
    hierarchy_view: TwoLevelPerformanceViewModel | None
    has_sweep_result: bool
    has_hierarchy_result: bool
    available_chart_metrics: tuple[PerformanceChartMetric, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.point_view_models, tuple):
            raise TypeError("point_view_models must be a tuple")
        if not isinstance(self.available_chart_metrics, tuple):
            raise TypeError("available_chart_metrics must be a tuple")
        if self.has_sweep_result != (self.sweep_result is not None):
            raise ValueError("has_sweep_result is inconsistent")
        if self.has_hierarchy_result != (self.hierarchy_result is not None):
            raise ValueError("has_hierarchy_result is inconsistent")
        sweep_values = (
            self.sweep_definition,
            self.selected_point_id,
            self.selected_point,
            self.chart_metric,
            self.chart_series,
            self.sweep_summary,
            self.comparison_view,
        )
        if self.has_sweep_result:
            if any(value is None for value in sweep_values):
                raise ValueError("completed sweep state requires all sweep views")
            selected = tuple(
                point for point in self.point_view_models if point.is_selected
            )
            if len(selected) != 1 or selected[0] != self.selected_point:
                raise ValueError("exactly one point view model must be selected")
        elif any(value is not None for value in sweep_values) or self.point_view_models:
            raise ValueError("empty sweep state must not retain sweep data")
        hierarchy_values = (
            self.hierarchy_model,
            self.hierarchy_result,
            self.hierarchy_view,
        )
        if self.has_hierarchy_result:
            if any(value is None for value in hierarchy_values):
                raise ValueError("completed hierarchy state requires all hierarchy views")
        elif any(value is not None for value in hierarchy_values):
            raise ValueError("empty hierarchy state must not retain hierarchy data")


EMPTY_PERFORMANCE_PAGE_STATE = PerformancePageState(
    sweep_definition=None,
    sweep_result=None,
    selected_point_id=None,
    selected_point=None,
    point_view_models=(),
    chart_metric=None,
    chart_series=None,
    sweep_summary=None,
    comparison_view=None,
    hierarchy_model=None,
    hierarchy_result=None,
    hierarchy_view=None,
    has_sweep_result=False,
    has_hierarchy_result=False,
    available_chart_metrics=tuple(PerformanceChartMetric),
)


__all__ = ["EMPTY_PERFORMANCE_PAGE_STATE", "PerformancePageState"]
