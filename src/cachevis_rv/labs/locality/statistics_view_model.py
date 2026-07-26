"""Invariant-aware cumulative statistics for Locality Lab presentation."""

from dataclasses import dataclass

from .model import LocalityStatistics


@dataclass(frozen=True)
class LocalityStatisticsViewModel:
    accesses: int
    hits: int
    misses: int
    unique_addresses: int
    unique_blocks: int
    first_touch_count: int
    spatial_count: int
    temporal_count: int
    same_block_transition_count: int
    hit_rate: float
    miss_rate: float
    spatial_event_rate: float
    temporal_event_rate: float
    average_address_reuse_gap: float | None
    average_block_reuse_gap: float | None
    average_block_reuse_distance: float | None
    partition_invariant_ok: bool
    address_invariant_ok: bool
    cache_invariant_ok: bool


def build_statistics_view_model(
    statistics: LocalityStatistics,
) -> LocalityStatisticsViewModel:
    """Publish raw values and explicit teaching invariants."""
    return LocalityStatisticsViewModel(
        **{
            name: getattr(statistics, name)
            for name in LocalityStatistics.__dataclass_fields__
        },
        partition_invariant_ok=(
            statistics.first_touch_count
            + statistics.spatial_count
            + statistics.temporal_count
            == statistics.accesses
        ),
        address_invariant_ok=(
            statistics.first_touch_count + statistics.spatial_count
            == statistics.unique_addresses
        ),
        cache_invariant_ok=(
            statistics.hits + statistics.misses == statistics.accesses
        ),
    )


__all__ = ["LocalityStatisticsViewModel", "build_statistics_view_model"]
