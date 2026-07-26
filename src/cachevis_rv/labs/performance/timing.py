"""Explicit cycle assumptions for the Performance Lab core."""

from dataclasses import dataclass
import math
from numbers import Real


def _finite_number(name: str, value: Real, *, positive: bool) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    if positive and result <= 0.0:
        raise ValueError(f"{name} must be positive")
    if not positive and result < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return result


@dataclass(frozen=True)
class PerformanceTimingModel:
    """User-supplied single-level cache timing assumptions."""

    hit_time_cycles: float
    fixed_miss_overhead_cycles: float
    transfer_cycles_per_byte: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "hit_time_cycles",
            _finite_number("hit_time_cycles", self.hit_time_cycles, positive=True),
        )
        object.__setattr__(
            self,
            "fixed_miss_overhead_cycles",
            _finite_number(
                "fixed_miss_overhead_cycles",
                self.fixed_miss_overhead_cycles,
                positive=False,
            ),
        )
        object.__setattr__(
            self,
            "transfer_cycles_per_byte",
            _finite_number(
                "transfer_cycles_per_byte",
                self.transfer_cycles_per_byte,
                positive=False,
            ),
        )

    def effective_miss_penalty(self, block_size_bytes: int) -> float:
        """Return the extra cycles paid by one miss after the lookup."""
        if (
            isinstance(block_size_bytes, bool)
            or not isinstance(block_size_bytes, int)
            or block_size_bytes <= 0
        ):
            raise ValueError("block_size_bytes must be a positive integer")
        try:
            penalty = (
                self.fixed_miss_overhead_cycles
                + block_size_bytes * self.transfer_cycles_per_byte
            )
        except OverflowError as exc:
            raise ValueError("effective miss penalty must be finite") from exc
        if not math.isfinite(penalty):
            raise ValueError("effective miss penalty must be finite")
        return penalty


__all__ = ["PerformanceTimingModel"]
