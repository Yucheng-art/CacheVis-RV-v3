"""Immutable value models for single-level performance experiments."""

from dataclasses import dataclass
import math
from numbers import Real

from cachevis_rv.core import CacheConfig

from .timing import PerformanceTimingModel


@dataclass(frozen=True)
class PerformanceCacheLineSnapshot:
    """Detached immutable copy of one simulator cache line."""

    set_index: int
    way: int
    valid: bool
    tag: int | None
    dirty: bool
    last_used: int
    insert_time: int


@dataclass(frozen=True)
class PerformanceMetrics:
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

    def __post_init__(self) -> None:
        for name in ("accesses", "hits", "misses", "line_fills", "bytes_fetched"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.hits + self.misses != self.accesses:
            raise ValueError("hits + misses must equal accesses")
        if self.line_fills != self.misses:
            raise ValueError("line_fills must equal misses")
        for name in (
            "hit_rate",
            "miss_rate",
            "hit_time_cycles",
            "effective_miss_penalty_cycles",
            "total_lookup_cycles",
            "total_miss_penalty_cycles",
            "total_cycles",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"{name} must be a real number")
            if not math.isfinite(float(value)) or float(value) < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")
        for name in ("amat_cycles", "bytes_fetched_per_access", "miss_stall_fraction"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, Real)
                or not math.isfinite(float(value))
                or float(value) < 0.0
            ):
                raise ValueError(f"{name} must be None or finite and non-negative")
        if not 0.0 <= self.hit_rate <= 1.0 or not 0.0 <= self.miss_rate <= 1.0:
            raise ValueError("rates must be between 0 and 1")
        expected_hit_rate = 0.0 if self.accesses == 0 else self.hits / self.accesses
        expected_miss_rate = 0.0 if self.accesses == 0 else self.misses / self.accesses
        if not math.isclose(self.hit_rate, expected_hit_rate) or not math.isclose(
            self.miss_rate, expected_miss_rate
        ):
            raise ValueError("hit and miss rates are inconsistent with counts")
        if not math.isclose(
            self.total_lookup_cycles,
            self.accesses * self.hit_time_cycles,
        ):
            raise ValueError("lookup cycles must equal accesses * hit time")
        if not math.isclose(
            self.total_miss_penalty_cycles,
            self.misses * self.effective_miss_penalty_cycles,
        ):
            raise ValueError("miss penalty cycles must equal misses * penalty")
        if not math.isclose(
            self.total_cycles,
            self.total_lookup_cycles + self.total_miss_penalty_cycles,
        ):
            raise ValueError("total cycle decomposition is inconsistent")
        if self.accesses:
            if self.amat_cycles is None:
                raise ValueError("non-empty metrics require AMAT")
            if not math.isclose(self.amat_cycles * self.accesses, self.total_cycles):
                raise ValueError("AMAT must equal total_cycles / accesses")
            if self.bytes_fetched_per_access is None:
                raise ValueError("non-empty metrics require average traffic")
            if not math.isclose(
                self.bytes_fetched_per_access,
                self.bytes_fetched / self.accesses,
            ):
                raise ValueError("average traffic is inconsistent")
        elif self.amat_cycles is not None or self.bytes_fetched_per_access is not None:
            raise ValueError("empty metrics use None for per-access averages")
        if self.total_cycles == 0.0:
            if self.miss_stall_fraction is not None:
                raise ValueError("zero-cycle metrics use None miss stall fraction")
        elif self.miss_stall_fraction is None or not math.isclose(
            self.miss_stall_fraction,
            self.total_miss_penalty_cycles / self.total_cycles,
        ):
            raise ValueError("miss stall fraction is inconsistent")


PerformanceCacheSnapshot = tuple[tuple[PerformanceCacheLineSnapshot, ...], ...]


@dataclass(frozen=True)
class PerformanceRunResult:
    config: CacheConfig
    timing: PerformanceTimingModel
    addresses: tuple[int, ...]
    metrics: PerformanceMetrics
    final_cache_snapshot: PerformanceCacheSnapshot


@dataclass(frozen=True)
class PerformanceRunSpec:
    point_id: str
    label: str
    x_value: int | float
    config: CacheConfig
    timing: PerformanceTimingModel

    def __post_init__(self) -> None:
        if not isinstance(self.point_id, str) or not self.point_id.strip():
            raise ValueError("point_id must be a non-empty string")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("label must be a non-empty string")
        if (
            isinstance(self.x_value, bool)
            or not isinstance(self.x_value, Real)
            or not math.isfinite(float(self.x_value))
        ):
            raise ValueError("x_value must be an int or finite float")
        if not isinstance(self.config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        if not isinstance(self.timing, PerformanceTimingModel):
            raise TypeError("timing must be a PerformanceTimingModel")


__all__ = [
    "PerformanceCacheLineSnapshot",
    "PerformanceCacheSnapshot",
    "PerformanceMetrics",
    "PerformanceRunResult",
    "PerformanceRunSpec",
]
