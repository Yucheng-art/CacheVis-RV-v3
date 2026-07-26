"""Completed-sweep ranking and hit-rate/AMAT tradeoff facts."""

from dataclasses import dataclass
import math

from .sweep import PerformanceSweepResult


@dataclass(frozen=True)
class PerformanceTradeoffPairViewModel:
    higher_hit_rate_point_id: str
    higher_hit_rate_label: str
    lower_hit_rate_point_id: str
    lower_hit_rate_label: str
    higher_hit_rate: float
    lower_hit_rate: float
    higher_amat: float
    lower_amat: float
    higher_hit_rate_has_worse_amat: bool
    explanation: str


@dataclass(frozen=True)
class PerformanceComparisonViewModel:
    hit_rate_amat_ranking_disagrees: bool
    tradeoff_pairs: tuple[PerformanceTradeoffPairViewModel, ...]
    baseline_point_id: str
    baseline_speedup: float | None
    fastest_point_ids: tuple[str, ...]
    fastest_point_labels: tuple[str, ...]
    slowest_point_ids: tuple[str, ...]
    slowest_point_labels: tuple[str, ...]
    maximum_speedup: float | None
    minimum_speedup: float | None
    all_total_cycles_equal: bool
    comparison_title: str
    teaching_insight: str


def build_comparison_view_model(
    result: PerformanceSweepResult,
) -> PerformanceComparisonViewModel:
    if not isinstance(result, PerformanceSweepResult):
        raise TypeError("result must be PerformanceSweepResult")
    points = result.point_results
    labels = {point.point_id: point.label for point in points}
    tradeoffs = _tradeoff_pairs(result)
    cycles = tuple(point.run_result.metrics.total_cycles for point in points)
    rankable = bool(cycles) and any(value > 0.0 for value in cycles)
    fastest_ids = _cycle_ties(points, minimum=True) if rankable else ()
    slowest_ids = _cycle_ties(points, minimum=False) if rankable else ()
    speedups = tuple(
        point.speedup_vs_baseline
        for point in points
        if point.speedup_vs_baseline is not None
    )
    baseline = next(point for point in points if point.point_id == result.baseline_point_id)
    disagrees = bool(tradeoffs)
    return PerformanceComparisonViewModel(
        hit_rate_amat_ranking_disagrees=disagrees,
        tradeoff_pairs=tradeoffs,
        baseline_point_id=result.baseline_point_id,
        baseline_speedup=baseline.speedup_vs_baseline,
        fastest_point_ids=fastest_ids,
        fastest_point_labels=tuple(labels[point_id] for point_id in fastest_ids),
        slowest_point_ids=slowest_ids,
        slowest_point_labels=tuple(labels[point_id] for point_id in slowest_ids),
        maximum_speedup=max(speedups) if speedups else None,
        minimum_speedup=min(speedups) if speedups else None,
        all_total_cycles_equal=(
            bool(cycles)
            and all(math.isclose(cycles[0], value) for value in cycles[1:])
        ),
        comparison_title=(
            "Hit rate and AMAT rankings disagree"
            if disagrees
            else "Completed sweep comparison"
        ),
        teaching_insight=(
            "A higher hit rate can still have worse AMAT under explicit timing assumptions."
            if disagrees
            else "These rankings describe only this completed trace and timing model, not every workload."
        ),
    )


def _tradeoff_pairs(
    result: PerformanceSweepResult,
) -> tuple[PerformanceTradeoffPairViewModel, ...]:
    pairs = []
    points = result.point_results
    for index, first in enumerate(points):
        for second in points[index + 1 :]:
            a = first.run_result.metrics
            b = second.run_result.metrics
            if a.amat_cycles is None or b.amat_cycles is None:
                continue
            if a.hit_rate > b.hit_rate and a.amat_cycles > b.amat_cycles:
                higher, lower = first, second
            elif b.hit_rate > a.hit_rate and b.amat_cycles > a.amat_cycles:
                higher, lower = second, first
            else:
                continue
            high_metrics = higher.run_result.metrics
            low_metrics = lower.run_result.metrics
            pairs.append(
                PerformanceTradeoffPairViewModel(
                    higher_hit_rate_point_id=higher.point_id,
                    higher_hit_rate_label=higher.label,
                    lower_hit_rate_point_id=lower.point_id,
                    lower_hit_rate_label=lower.label,
                    higher_hit_rate=high_metrics.hit_rate,
                    lower_hit_rate=low_metrics.hit_rate,
                    higher_amat=high_metrics.amat_cycles,
                    lower_amat=low_metrics.amat_cycles,
                    higher_hit_rate_has_worse_amat=True,
                    explanation=(
                        f"{higher.label} has hit rate {high_metrics.hit_rate} but AMAT "
                        f"{high_metrics.amat_cycles}, worse than {lower.label}'s AMAT "
                        f"{low_metrics.amat_cycles} for this trace."
                    ),
                )
            )
    return tuple(pairs)


def _cycle_ties(points, *, minimum: bool) -> tuple[str, ...]:
    cycles = tuple(point.run_result.metrics.total_cycles for point in points)
    best = (min if minimum else max)(cycles)
    return tuple(
        point.point_id
        for point in points
        if math.isclose(point.run_result.metrics.total_cycles, best)
    )


__all__ = [
    "PerformanceComparisonViewModel",
    "PerformanceTradeoffPairViewModel",
    "build_comparison_view_model",
]
