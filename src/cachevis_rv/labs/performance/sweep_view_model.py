"""Point rows and factual summary models for completed sweeps."""

from dataclasses import dataclass
import math

from cachevis_rv.core import CacheConfig

from .metrics_view_model import PerformanceMetricsViewModel, build_metrics_view_model
from .sweep import PerformanceSweepKind, PerformanceSweepResult
from .timing import PerformanceTimingModel


@dataclass(frozen=True)
class PerformanceSweepPointViewModel:
    point_id: str
    label: str
    x_value: int | float
    config: CacheConfig
    timing: PerformanceTimingModel
    metrics: PerformanceMetricsViewModel
    amat_delta_vs_baseline: float | None
    total_cycles_delta_vs_baseline: float
    speedup_vs_baseline: float | None
    is_baseline: bool
    is_selected: bool
    is_best_amat: bool
    is_best_hit_rate: bool
    is_lowest_traffic: bool


@dataclass(frozen=True)
class PerformanceSweepSummaryViewModel:
    sweep_id: str
    title: str
    description: str
    sweep_kind: PerformanceSweepKind
    baseline_point_id: str
    baseline_label: str
    point_count: int
    best_amat_point_ids: tuple[str, ...]
    best_amat_labels: tuple[str, ...]
    best_hit_rate_point_ids: tuple[str, ...]
    best_hit_rate_labels: tuple[str, ...]
    lowest_traffic_point_ids: tuple[str, ...]
    lowest_traffic_labels: tuple[str, ...]
    best_amat_is_tie: bool
    best_hit_rate_is_tie: bool
    lowest_traffic_is_tie: bool
    hit_rate_and_amat_best_agree: bool
    expected_teaching_conclusion: str
    actual_observations: tuple[str, ...]


def build_sweep_point_view_models(
    result: PerformanceSweepResult,
    selected_point_id: str,
) -> tuple[PerformanceSweepPointViewModel, ...]:
    if not isinstance(result, PerformanceSweepResult):
        raise TypeError("result must be PerformanceSweepResult")
    point_ids = {point.point_id for point in result.point_results}
    if selected_point_id not in point_ids:
        raise ValueError(f"unknown performance point_id: {selected_point_id}")
    return tuple(
        PerformanceSweepPointViewModel(
            point_id=point.point_id,
            label=point.label,
            x_value=point.x_value,
            config=point.run_result.config,
            timing=point.run_result.timing,
            metrics=build_metrics_view_model(point.run_result.metrics),
            amat_delta_vs_baseline=point.amat_delta_vs_baseline,
            total_cycles_delta_vs_baseline=point.total_cycles_delta_vs_baseline,
            speedup_vs_baseline=point.speedup_vs_baseline,
            is_baseline=point.point_id == result.baseline_point_id,
            is_selected=point.point_id == selected_point_id,
            is_best_amat=point.point_id in result.best_amat_point_ids,
            is_best_hit_rate=point.point_id in result.best_hit_rate_point_ids,
            is_lowest_traffic=point.point_id in result.lowest_traffic_point_ids,
        )
        for point in result.point_results
    )


def build_sweep_summary_view_model(
    result: PerformanceSweepResult,
) -> PerformanceSweepSummaryViewModel:
    if not isinstance(result, PerformanceSweepResult):
        raise TypeError("result must be PerformanceSweepResult")
    labels = {point.point_id: point.label for point in result.point_results}
    definition = result.definition
    return PerformanceSweepSummaryViewModel(
        sweep_id=definition.sweep_id,
        title=definition.title,
        description=definition.description,
        sweep_kind=definition.kind,
        baseline_point_id=result.baseline_point_id,
        baseline_label=labels[result.baseline_point_id],
        point_count=len(result.point_results),
        best_amat_point_ids=result.best_amat_point_ids,
        best_amat_labels=_labels(result.best_amat_point_ids, labels),
        best_hit_rate_point_ids=result.best_hit_rate_point_ids,
        best_hit_rate_labels=_labels(result.best_hit_rate_point_ids, labels),
        lowest_traffic_point_ids=result.lowest_traffic_point_ids,
        lowest_traffic_labels=_labels(result.lowest_traffic_point_ids, labels),
        best_amat_is_tie=len(result.best_amat_point_ids) > 1,
        best_hit_rate_is_tie=len(result.best_hit_rate_point_ids) > 1,
        lowest_traffic_is_tie=len(result.lowest_traffic_point_ids) > 1,
        hit_rate_and_amat_best_agree=(
            set(result.best_amat_point_ids) == set(result.best_hit_rate_point_ids)
            and bool(result.best_amat_point_ids)
        ),
        expected_teaching_conclusion=definition.expected_teaching_conclusion,
        actual_observations=_actual_observations(result),
    )


def _labels(point_ids: tuple[str, ...], labels: dict[str, str]) -> tuple[str, ...]:
    return tuple(labels[point_id] for point_id in point_ids)


def _actual_observations(result: PerformanceSweepResult) -> tuple[str, ...]:
    points = result.point_results
    observations: list[str] = []
    labels = {point.point_id: point.label for point in points}
    if len(result.best_amat_point_ids) > 1:
        value = next(
            point.run_result.metrics.amat_cycles
            for point in points
            if point.point_id == result.best_amat_point_ids[0]
        )
        observations.append(
            f"AMAT tie at {value} cycles: "
            + ", ".join(_labels(result.best_amat_point_ids, labels))
            + "."
        )
    misses = tuple(point.run_result.metrics.misses for point in points)
    if len(set(misses)) == 1:
        observations.append(f"All points produced {misses[0]} misses.")
    elif points:
        minimum = min(misses)
        maximum = max(misses)
        low_labels = tuple(
            point.label for point in points if point.run_result.metrics.misses == minimum
        )
        observations.append(
            f"Observed misses range from {minimum} to {maximum}; lowest: "
            + ", ".join(low_labels)
            + "."
        )
    penalties = tuple(
        point.run_result.metrics.effective_miss_penalty_cycles for point in points
    )
    if len(set(penalties)) > 1:
        observations.append(
            f"Effective miss penalty ranges from {min(penalties)} to {max(penalties)} cycles."
        )
    amats = tuple(
        point.run_result.metrics.amat_cycles
        for point in points
        if point.run_result.metrics.amat_cycles is not None
    )
    if amats and not all(math.isclose(amats[0], value) for value in amats[1:]):
        observations.append(f"Observed AMAT ranges from {min(amats)} to {max(amats)} cycles.")
    for higher in points:
        for lower in points:
            if (
                higher.point_id != lower.point_id
                and higher.run_result.metrics.hit_rate > lower.run_result.metrics.hit_rate
                and higher.run_result.metrics.amat_cycles is not None
                and lower.run_result.metrics.amat_cycles is not None
                and higher.run_result.metrics.amat_cycles > lower.run_result.metrics.amat_cycles
            ):
                observation = (
                    f"{higher.label} has a higher hit rate but a worse AMAT than {lower.label}."
                )
                if observation not in observations:
                    observations.append(observation)
    traffic = tuple(point.run_result.metrics.bytes_fetched for point in points)
    if traffic:
        minimum_traffic = min(traffic)
        observations.append(
            f"Lowest observed traffic is {minimum_traffic} bytes: "
            + ", ".join(_labels(result.lowest_traffic_point_ids, labels))
            + "."
        )
    return tuple(observations)


__all__ = [
    "PerformanceSweepPointViewModel",
    "PerformanceSweepSummaryViewModel",
    "build_sweep_point_view_models",
    "build_sweep_summary_view_model",
]
