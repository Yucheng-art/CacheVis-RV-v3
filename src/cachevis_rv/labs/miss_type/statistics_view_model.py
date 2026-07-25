"""Presentation-ready cumulative 3C statistics."""

from dataclasses import dataclass

from .model import MissTypeStatistics


@dataclass(frozen=True)
class MissTypeStatisticsViewModel:
    """Formatted statistics without GUI dependencies."""

    accesses: int
    hits: int
    misses: int
    compulsory: int
    conflict: int
    capacity: int
    hit_rate_text: str
    miss_rate_text: str
    invariant_text: str
    invariant_valid: bool


def build_statistics_view_model(
    statistics: MissTypeStatistics,
) -> MissTypeStatisticsViewModel:
    """Format authoritative session statistics without recomputing classification."""
    classified_total = (
        statistics.hits
        + statistics.compulsory_misses
        + statistics.conflict_misses
        + statistics.capacity_misses
    )
    valid = classified_total == statistics.accesses
    return MissTypeStatisticsViewModel(
        accesses=statistics.accesses,
        hits=statistics.hits,
        misses=statistics.misses,
        compulsory=statistics.compulsory_misses,
        conflict=statistics.conflict_misses,
        capacity=statistics.capacity_misses,
        hit_rate_text=f"{statistics.hit_rate:.1%}",
        miss_rate_text=f"{statistics.miss_rate:.1%}",
        invariant_text=(
            "Hits + C + F + A = Accesses"
            if valid
            else "Statistics invariant failed"
        ),
        invariant_valid=valid,
    )


__all__ = [
    "MissTypeStatisticsViewModel",
    "build_statistics_view_model",
]
