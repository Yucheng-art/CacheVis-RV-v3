"""Single-variable configuration sweeps for the Performance Lab core."""

from dataclasses import dataclass
from enum import Enum
import math

from .model import PerformanceRunResult, PerformanceRunSpec
from .runner import PerformanceRunner


class PerformanceSweepKind(str, Enum):
    CACHE_SIZE = "cache_size"
    BLOCK_SIZE = "block_size"
    ASSOCIATIVITY = "associativity"
    MISS_PENALTY = "miss_penalty"
    HIT_TIME = "hit_time"
    CUSTOM = "custom"


@dataclass(frozen=True)
class PerformanceSweepDefinition:
    sweep_id: str
    title: str
    description: str
    kind: PerformanceSweepKind
    addresses: tuple[int, ...]
    points: tuple[PerformanceRunSpec, ...]
    baseline_point_id: str
    expected_teaching_conclusion: str

    def __post_init__(self) -> None:
        if not isinstance(self.sweep_id, str) or not self.sweep_id.strip():
            raise ValueError("sweep_id must be a non-empty string")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")
        if not isinstance(self.expected_teaching_conclusion, str) or not self.expected_teaching_conclusion.strip():
            raise ValueError("expected_teaching_conclusion must be a non-empty string")
        if not isinstance(self.kind, PerformanceSweepKind):
            raise TypeError("kind must be a PerformanceSweepKind")
        object.__setattr__(self, "addresses", tuple(self.addresses))
        object.__setattr__(self, "points", tuple(self.points))
        if not self.points:
            raise ValueError("a sweep requires at least one point")
        if any(not isinstance(point, PerformanceRunSpec) for point in self.points):
            raise TypeError("points must contain PerformanceRunSpec values")
        point_ids = tuple(point.point_id for point in self.points)
        if len(set(point_ids)) != len(point_ids):
            raise ValueError("point_id values must be unique within a sweep")
        if self.baseline_point_id not in point_ids:
            raise ValueError("baseline_point_id must identify an existing point")


@dataclass(frozen=True)
class PerformanceSweepPointResult:
    point_id: str
    label: str
    x_value: int | float
    run_result: PerformanceRunResult
    amat_delta_vs_baseline: float | None
    total_cycles_delta_vs_baseline: float
    speedup_vs_baseline: float | None


@dataclass(frozen=True)
class PerformanceSweepResult:
    definition: PerformanceSweepDefinition
    point_results: tuple[PerformanceSweepPointResult, ...]
    best_amat_point_ids: tuple[str, ...]
    best_hit_rate_point_ids: tuple[str, ...]
    lowest_traffic_point_ids: tuple[str, ...]
    baseline_point_id: str


class PerformanceSweepRunner:
    """Validate a sweep and execute each point as an independent cold run."""

    def __init__(self, runner: PerformanceRunner | None = None) -> None:
        self._runner = runner if runner is not None else PerformanceRunner()

    def run(self, definition: PerformanceSweepDefinition) -> PerformanceSweepResult:
        if not isinstance(definition, PerformanceSweepDefinition):
            raise TypeError("definition must be a PerformanceSweepDefinition")
        self._validate_dimension(definition)
        runs = tuple(
            self._runner.run(point.config, definition.addresses, point.timing)
            for point in definition.points
        )
        baseline_index = next(
            index
            for index, point in enumerate(definition.points)
            if point.point_id == definition.baseline_point_id
        )
        baseline = runs[baseline_index].metrics
        point_results = tuple(
            self._build_point_result(point, run, baseline)
            for point, run in zip(definition.points, runs)
        )
        return PerformanceSweepResult(
            definition=definition,
            point_results=point_results,
            best_amat_point_ids=_best_ids(
                point_results,
                lambda point: point.run_result.metrics.amat_cycles,
                minimum=True,
            ),
            best_hit_rate_point_ids=_best_ids(
                point_results,
                lambda point: point.run_result.metrics.hit_rate,
                minimum=False,
            ),
            lowest_traffic_point_ids=_best_ids(
                point_results,
                lambda point: float(point.run_result.metrics.bytes_fetched),
                minimum=True,
            ),
            baseline_point_id=definition.baseline_point_id,
        )

    @staticmethod
    def _build_point_result(point, run, baseline) -> PerformanceSweepPointResult:
        metrics = run.metrics
        amat_delta = (
            None
            if metrics.amat_cycles is None or baseline.amat_cycles is None
            else metrics.amat_cycles - baseline.amat_cycles
        )
        speedup = (
            None
            if metrics.total_cycles == 0.0 or baseline.total_cycles == 0.0
            else baseline.total_cycles / metrics.total_cycles
        )
        return PerformanceSweepPointResult(
            point_id=point.point_id,
            label=point.label,
            x_value=point.x_value,
            run_result=run,
            amat_delta_vs_baseline=amat_delta,
            total_cycles_delta_vs_baseline=(
                metrics.total_cycles - baseline.total_cycles
            ),
            speedup_vs_baseline=speedup,
        )

    @staticmethod
    def _validate_dimension(definition: PerformanceSweepDefinition) -> None:
        baseline = definition.points[0]
        for point in definition.points:
            if point.config.replacement_policy not in {"LRU", "FIFO"}:
                raise ValueError("all sweep points must use LRU or FIFO")
        kind = definition.kind
        if kind is PerformanceSweepKind.CUSTOM:
            return
        for point in definition.points[1:]:
            if kind is PerformanceSweepKind.CACHE_SIZE:
                _require_config_equal_except(baseline, point, {"cache_size_bytes"})
                _require_equal_timing(baseline, point)
            elif kind is PerformanceSweepKind.BLOCK_SIZE:
                _require_config_equal_except(baseline, point, {"block_size_bytes"})
                _require_equal_timing(baseline, point)
            elif kind is PerformanceSweepKind.ASSOCIATIVITY:
                _require_config_equal_except(baseline, point, {"ways"})
                _require_equal_timing(baseline, point)
            elif kind is PerformanceSweepKind.MISS_PENALTY:
                if point.config != baseline.config:
                    raise ValueError("MISS_PENALTY sweep requires identical configs")
                if (
                    point.timing.hit_time_cycles
                    != baseline.timing.hit_time_cycles
                    or point.timing.transfer_cycles_per_byte
                    != baseline.timing.transfer_cycles_per_byte
                ):
                    raise ValueError(
                        "MISS_PENALTY sweep may vary only fixed miss overhead"
                    )
            elif kind is PerformanceSweepKind.HIT_TIME:
                if point.config != baseline.config:
                    raise ValueError("HIT_TIME sweep requires identical configs")
                if (
                    point.timing.fixed_miss_overhead_cycles
                    != baseline.timing.fixed_miss_overhead_cycles
                    or point.timing.transfer_cycles_per_byte
                    != baseline.timing.transfer_cycles_per_byte
                ):
                    raise ValueError("HIT_TIME sweep may vary only hit time")


def _require_config_equal_except(
    baseline: PerformanceRunSpec,
    point: PerformanceRunSpec,
    allowed: set[str],
) -> None:
    fields = (
        "cache_size_bytes",
        "block_size_bytes",
        "ways",
        "replacement_policy",
        "write_policy",
        "address_bits",
    )
    changed = {
        name
        for name in fields
        if getattr(baseline.config, name) != getattr(point.config, name)
    }
    if not changed.issubset(allowed):
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"sweep may vary only {allowed_text}; changed {sorted(changed)}")


def _require_equal_timing(
    baseline: PerformanceRunSpec,
    point: PerformanceRunSpec,
) -> None:
    if point.timing != baseline.timing:
        raise ValueError("this sweep kind requires identical timing inputs")


def _best_ids(point_results, value_getter, *, minimum: bool) -> tuple[str, ...]:
    available = tuple(
        (point.point_id, value_getter(point))
        for point in point_results
        if value_getter(point) is not None
    )
    if not available:
        return ()
    best = (min if minimum else max)(value for _, value in available)
    return tuple(
        point_id
        for point_id, value in available
        if math.isclose(value, best, rel_tol=1e-12, abs_tol=1e-12)
    )


__all__ = [
    "PerformanceSweepDefinition",
    "PerformanceSweepKind",
    "PerformanceSweepPointResult",
    "PerformanceSweepResult",
    "PerformanceSweepRunner",
]
