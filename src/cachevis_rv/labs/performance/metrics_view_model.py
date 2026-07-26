"""Presentation-safe mapping of formal performance metrics."""

from dataclasses import dataclass
import math

from .model import PerformanceMetrics


@dataclass(frozen=True)
class PerformanceMetricsViewModel:
    accesses: int
    hits: int
    misses: int
    hit_rate: float
    miss_rate: float
    hit_time_cycles: float
    effective_miss_penalty_cycles: float
    total_lookup_cycles: float
    total_miss_penalty_cycles: float
    total_cycles: float
    amat_cycles: float | None
    line_fills: int
    bytes_fetched: int
    bytes_fetched_per_access: float | None
    miss_stall_fraction: float | None
    access_invariant_ok: bool
    cycle_decomposition_ok: bool
    amat_invariant_ok: bool
    traffic_invariant_ok: bool

    @property
    def amat_display(self) -> str:
        return _display(self.amat_cycles)

    @property
    def bytes_per_access_display(self) -> str:
        return _display(self.bytes_fetched_per_access)

    @property
    def miss_stall_fraction_display(self) -> str:
        return _display(self.miss_stall_fraction)


def build_metrics_view_model(
    metrics: PerformanceMetrics,
) -> PerformanceMetricsViewModel:
    if not isinstance(metrics, PerformanceMetrics):
        raise TypeError("metrics must be PerformanceMetrics")
    return PerformanceMetricsViewModel(
        accesses=metrics.accesses,
        hits=metrics.hits,
        misses=metrics.misses,
        hit_rate=metrics.hit_rate,
        miss_rate=metrics.miss_rate,
        hit_time_cycles=metrics.hit_time_cycles,
        effective_miss_penalty_cycles=metrics.effective_miss_penalty_cycles,
        total_lookup_cycles=metrics.total_lookup_cycles,
        total_miss_penalty_cycles=metrics.total_miss_penalty_cycles,
        total_cycles=metrics.total_cycles,
        amat_cycles=metrics.amat_cycles,
        line_fills=metrics.line_fills,
        bytes_fetched=metrics.bytes_fetched,
        bytes_fetched_per_access=metrics.bytes_fetched_per_access,
        miss_stall_fraction=metrics.miss_stall_fraction,
        access_invariant_ok=(metrics.hits + metrics.misses == metrics.accesses),
        cycle_decomposition_ok=math.isclose(
            metrics.total_cycles,
            metrics.total_lookup_cycles + metrics.total_miss_penalty_cycles,
        ),
        amat_invariant_ok=(
            metrics.amat_cycles is None
            if metrics.accesses == 0
            else math.isclose(
                metrics.amat_cycles * metrics.accesses,
                metrics.total_cycles,
            )
        ),
        traffic_invariant_ok=(metrics.line_fills == metrics.misses),
    )


def _display(value: float | None) -> str:
    return "N/A" if value is None else str(value)


__all__ = ["PerformanceMetricsViewModel", "build_metrics_view_model"]
