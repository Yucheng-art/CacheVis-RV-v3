"""Chart-ready values without plotting-library or Qt dependencies."""

from dataclasses import dataclass
from enum import Enum
import math

from .sweep import PerformanceSweepKind, PerformanceSweepResult


class PerformanceChartMetric(str, Enum):
    AMAT = "amat"
    HIT_RATE = "hit_rate"
    MISS_RATE = "miss_rate"
    TOTAL_CYCLES = "total_cycles"
    BYTES_FETCHED = "bytes_fetched"
    MISS_STALL_FRACTION = "miss_stall_fraction"
    SPEEDUP = "speedup"


@dataclass(frozen=True)
class PerformanceChartPointViewModel:
    point_id: str
    label: str
    x_value: int | float
    y_value: int | float | None
    is_baseline: bool
    is_selected: bool
    is_best_for_metric: bool


@dataclass(frozen=True)
class PerformanceChartSeriesViewModel:
    metric: PerformanceChartMetric
    title: str
    x_axis_label: str
    y_axis_label: str
    points: tuple[PerformanceChartPointViewModel, ...]
    best_point_ids: tuple[str, ...]
    has_missing_values: bool


def build_chart_series_view_model(
    result: PerformanceSweepResult,
    metric: PerformanceChartMetric,
    selected_point_id: str,
) -> PerformanceChartSeriesViewModel:
    if not isinstance(result, PerformanceSweepResult):
        raise TypeError("result must be PerformanceSweepResult")
    if not isinstance(metric, PerformanceChartMetric):
        raise ValueError("metric must be a PerformanceChartMetric")
    point_ids = {point.point_id for point in result.point_results}
    if selected_point_id not in point_ids:
        raise ValueError(f"unknown performance point_id: {selected_point_id}")
    values = tuple(_metric_value(point, metric) for point in result.point_results)
    best_ids = _best_ids(result, values, metric)
    points = tuple(
        PerformanceChartPointViewModel(
            point_id=point.point_id,
            label=point.label,
            x_value=point.x_value,
            y_value=value,
            is_baseline=point.point_id == result.baseline_point_id,
            is_selected=point.point_id == selected_point_id,
            is_best_for_metric=point.point_id in best_ids,
        )
        for point, value in zip(result.point_results, values)
    )
    title, y_axis_label = _metric_labels(metric)
    return PerformanceChartSeriesViewModel(
        metric=metric,
        title=title,
        x_axis_label=_x_axis_label(result.definition.kind),
        y_axis_label=y_axis_label,
        points=points,
        best_point_ids=best_ids,
        has_missing_values=any(value is None for value in values),
    )


def _metric_value(point, metric: PerformanceChartMetric):
    metrics = point.run_result.metrics
    return {
        PerformanceChartMetric.AMAT: metrics.amat_cycles,
        PerformanceChartMetric.HIT_RATE: metrics.hit_rate,
        PerformanceChartMetric.MISS_RATE: metrics.miss_rate,
        PerformanceChartMetric.TOTAL_CYCLES: metrics.total_cycles,
        PerformanceChartMetric.BYTES_FETCHED: metrics.bytes_fetched,
        PerformanceChartMetric.MISS_STALL_FRACTION: metrics.miss_stall_fraction,
        PerformanceChartMetric.SPEEDUP: point.speedup_vs_baseline,
    }[metric]


def _best_ids(result, values, metric) -> tuple[str, ...]:
    available = tuple(
        (point.point_id, float(value))
        for point, value in zip(result.point_results, values)
        if value is not None
    )
    if not available:
        return ()
    higher_is_better = metric in {
        PerformanceChartMetric.HIT_RATE,
        PerformanceChartMetric.SPEEDUP,
    }
    best = (max if higher_is_better else min)(value for _, value in available)
    return tuple(
        point_id
        for point_id, value in available
        if math.isclose(value, best, rel_tol=1e-12, abs_tol=1e-12)
    )


def _x_axis_label(kind: PerformanceSweepKind) -> str:
    return {
        PerformanceSweepKind.CACHE_SIZE: "Cache Size (bytes)",
        PerformanceSweepKind.BLOCK_SIZE: "Block Size (bytes)",
        PerformanceSweepKind.ASSOCIATIVITY: "Associativity (ways)",
        PerformanceSweepKind.MISS_PENALTY: "Fixed Miss Overhead (cycles)",
        PerformanceSweepKind.HIT_TIME: "Hit Time (cycles)",
        PerformanceSweepKind.CUSTOM: "Sweep Value",
    }[kind]


def _metric_labels(metric: PerformanceChartMetric) -> tuple[str, str]:
    return {
        PerformanceChartMetric.AMAT: ("Average Memory Access Time", "AMAT (cycles)"),
        PerformanceChartMetric.HIT_RATE: ("Hit Rate", "Hit Rate"),
        PerformanceChartMetric.MISS_RATE: ("Miss Rate", "Miss Rate"),
        PerformanceChartMetric.TOTAL_CYCLES: ("Total Modeled Cycles", "Cycles"),
        PerformanceChartMetric.BYTES_FETCHED: ("Memory Fill Traffic", "Bytes Fetched"),
        PerformanceChartMetric.MISS_STALL_FRACTION: ("Miss Stall Fraction", "Fraction"),
        PerformanceChartMetric.SPEEDUP: ("Speedup vs Baseline", "Speedup"),
    }[metric]


__all__ = [
    "PerformanceChartMetric",
    "PerformanceChartPointViewModel",
    "PerformanceChartSeriesViewModel",
    "build_chart_series_view_model",
]
