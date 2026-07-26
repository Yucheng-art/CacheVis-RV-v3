"""Pure-Python orchestration for sweep and analytical hierarchy state."""

from dataclasses import replace

from .chart_view_model import PerformanceChartMetric, build_chart_series_view_model
from .comparison_view_model import build_comparison_view_model
from .hierarchy import TwoLevelPerformanceAnalyzer, TwoLevelTimingModel
from .hierarchy_view_model import build_hierarchy_view_model
from .page_state import EMPTY_PERFORMANCE_PAGE_STATE, PerformancePageState
from .sweep import PerformanceSweepDefinition, PerformanceSweepRunner
from .sweep_view_model import (
    build_sweep_point_view_models,
    build_sweep_summary_view_model,
)


class PerformanceController:
    """Manage immutable page state without GUI or simulator-level logic."""

    def __init__(self, sweep_runner=None, hierarchy_analyzer=None) -> None:
        self._sweep_runner = (
            sweep_runner if sweep_runner is not None else PerformanceSweepRunner()
        )
        self._hierarchy_analyzer = (
            hierarchy_analyzer
            if hierarchy_analyzer is not None
            else TwoLevelPerformanceAnalyzer()
        )
        self._state = EMPTY_PERFORMANCE_PAGE_STATE

    @property
    def state(self) -> PerformancePageState:
        return self._state

    def get_state(self) -> PerformancePageState:
        return self._state

    def run_sweep(
        self,
        definition: PerformanceSweepDefinition,
    ) -> PerformancePageState:
        if not isinstance(definition, PerformanceSweepDefinition):
            raise TypeError("definition must be a PerformanceSweepDefinition")
        result = self._sweep_runner.run(definition)
        selected_point_id = result.baseline_point_id
        points = build_sweep_point_view_models(result, selected_point_id)
        metric = PerformanceChartMetric.AMAT
        self._state = replace(
            self._state,
            sweep_definition=definition,
            sweep_result=result,
            selected_point_id=selected_point_id,
            selected_point=_selected(points),
            point_view_models=points,
            chart_metric=metric,
            chart_series=build_chart_series_view_model(
                result, metric, selected_point_id
            ),
            sweep_summary=build_sweep_summary_view_model(result),
            comparison_view=build_comparison_view_model(result),
            has_sweep_result=True,
        )
        return self._state

    def select_point(self, point_id: str) -> PerformancePageState:
        result = self._require_sweep_result()
        if point_id not in {point.point_id for point in result.point_results}:
            raise ValueError(f"unknown performance point_id: {point_id}")
        points = build_sweep_point_view_models(result, point_id)
        self._state = replace(
            self._state,
            selected_point_id=point_id,
            selected_point=_selected(points),
            point_view_models=points,
            chart_series=build_chart_series_view_model(
                result,
                self._state.chart_metric,
                point_id,
            ),
        )
        return self._state

    def select_chart_metric(
        self,
        metric: PerformanceChartMetric,
    ) -> PerformancePageState:
        if not isinstance(metric, PerformanceChartMetric):
            raise ValueError("metric must be a PerformanceChartMetric")
        result = self._require_sweep_result()
        self._state = replace(
            self._state,
            chart_metric=metric,
            chart_series=build_chart_series_view_model(
                result,
                metric,
                self._state.selected_point_id,
            ),
        )
        return self._state

    def analyze_hierarchy(
        self,
        model: TwoLevelTimingModel,
    ) -> PerformancePageState:
        if not isinstance(model, TwoLevelTimingModel):
            raise TypeError("model must be a TwoLevelTimingModel")
        result = self._hierarchy_analyzer.analyze(model)
        self._state = replace(
            self._state,
            hierarchy_model=model,
            hierarchy_result=result,
            hierarchy_view=build_hierarchy_view_model(result),
            has_hierarchy_result=True,
        )
        return self._state

    def clear_sweep(self) -> PerformancePageState:
        self._state = replace(
            self._state,
            sweep_definition=None,
            sweep_result=None,
            selected_point_id=None,
            selected_point=None,
            point_view_models=(),
            chart_metric=None,
            chart_series=None,
            sweep_summary=None,
            comparison_view=None,
            has_sweep_result=False,
        )
        return self._state

    def clear_hierarchy(self) -> PerformancePageState:
        self._state = replace(
            self._state,
            hierarchy_model=None,
            hierarchy_result=None,
            hierarchy_view=None,
            has_hierarchy_result=False,
        )
        return self._state

    def clear_all(self) -> PerformancePageState:
        self._state = EMPTY_PERFORMANCE_PAGE_STATE
        return self._state

    def _require_sweep_result(self):
        if self._state.sweep_result is None:
            raise RuntimeError("no completed performance sweep is available")
        return self._state.sweep_result


def _selected(points):
    return next(point for point in points if point.is_selected)


__all__ = ["PerformanceController"]
