"""Analytical two-level AMAT model; no L2 cache contents are simulated."""

from dataclasses import dataclass
import math
from numbers import Real


def _finite(name: str, value: Real, *, positive: bool = False) -> float:
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
class TwoLevelTimingModel:
    l1_hit_time_cycles: float
    l1_miss_rate: float
    l2_hit_time_cycles: float
    l2_local_miss_rate: float
    memory_penalty_cycles: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "l1_hit_time_cycles", _finite("l1_hit_time_cycles", self.l1_hit_time_cycles, positive=True))
        object.__setattr__(self, "l2_hit_time_cycles", _finite("l2_hit_time_cycles", self.l2_hit_time_cycles, positive=True))
        object.__setattr__(self, "memory_penalty_cycles", _finite("memory_penalty_cycles", self.memory_penalty_cycles))
        for name in ("l1_miss_rate", "l2_local_miss_rate"):
            value = _finite(name, getattr(self, name))
            if value > 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class TwoLevelPerformanceResult:
    model: TwoLevelTimingModel
    l1_hit_probability: float
    l2_hit_probability_global: float
    memory_access_probability: float
    l2_global_miss_rate: float
    l1_contribution_cycles: float
    l2_contribution_cycles: float
    memory_contribution_cycles: float
    amat_cycles: float
    probability_partition_ok: bool
    contribution_sum_ok: bool


class TwoLevelPerformanceAnalyzer:
    """Evaluate the formal sequential L1/L2 analytical equations."""

    @staticmethod
    def analyze(model: TwoLevelTimingModel) -> TwoLevelPerformanceResult:
        if not isinstance(model, TwoLevelTimingModel):
            raise TypeError("model must be a TwoLevelTimingModel")
        l1_hit_probability = 1.0 - model.l1_miss_rate
        l2_hit_probability_global = model.l1_miss_rate * (
            1.0 - model.l2_local_miss_rate
        )
        memory_access_probability = (
            model.l1_miss_rate * model.l2_local_miss_rate
        )
        l1_contribution = model.l1_hit_time_cycles
        l2_contribution = model.l1_miss_rate * model.l2_hit_time_cycles
        memory_contribution = (
            model.l1_miss_rate
            * model.l2_local_miss_rate
            * model.memory_penalty_cycles
        )
        amat = l1_contribution + l2_contribution + memory_contribution
        calculated = (
            l1_hit_probability,
            l2_hit_probability_global,
            memory_access_probability,
            l1_contribution,
            l2_contribution,
            memory_contribution,
            amat,
        )
        if not all(math.isfinite(value) for value in calculated):
            raise ValueError("two-level analytical results must be finite")
        return TwoLevelPerformanceResult(
            model=model,
            l1_hit_probability=l1_hit_probability,
            l2_hit_probability_global=l2_hit_probability_global,
            memory_access_probability=memory_access_probability,
            l2_global_miss_rate=memory_access_probability,
            l1_contribution_cycles=l1_contribution,
            l2_contribution_cycles=l2_contribution,
            memory_contribution_cycles=memory_contribution,
            amat_cycles=amat,
            probability_partition_ok=math.isclose(
                l1_hit_probability
                + l2_hit_probability_global
                + memory_access_probability,
                1.0,
            ),
            contribution_sum_ok=math.isclose(
                l1_contribution + l2_contribution + memory_contribution,
                amat,
            ),
        )


__all__ = [
    "TwoLevelPerformanceAnalyzer",
    "TwoLevelPerformanceResult",
    "TwoLevelTimingModel",
]
