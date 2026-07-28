"""Immutable cumulative statistics views."""

from dataclasses import dataclass

from .model import WritePolicyLaneStatistics


@dataclass(frozen=True)
class WritePolicyLaneStatisticsViewModel:
    lane_id: str
    lane_label: str
    accesses: int
    reads: int
    writes: int
    hits: int
    misses: int
    hit_rate: float
    miss_rate: float
    read_hits: int
    read_misses: int
    write_hits: int
    write_misses: int
    write_miss_allocations: int
    write_miss_bypasses: int
    block_fills: int
    clean_evictions: int
    dirty_evictions: int
    immediate_store_writes: int
    bypass_writes: int
    dirty_writebacks: int
    memory_read_transactions: int
    memory_read_bytes: int
    memory_write_transactions: int
    memory_write_bytes: int
    total_lower_memory_transactions: int
    total_lower_memory_bytes: int
    final_dirty_lines: int
    final_dirty_bytes: int
    memory_write_bytes_with_final_drain: int
    total_lower_memory_bytes_with_final_drain: int
    access_partition_ok: bool
    read_partition_ok: bool
    write_partition_ok: bool
    write_miss_partition_ok: bool
    fill_relation_ok: bool
    dirty_writeback_relation_ok: bool
    runtime_traffic_relation_ok: bool
    final_drain_relation_ok: bool


def build_lane_statistics_view_model(
    statistics: WritePolicyLaneStatistics,
) -> WritePolicyLaneStatisticsViewModel:
    if not isinstance(statistics, WritePolicyLaneStatistics):
        raise ValueError("statistics must be WritePolicyLaneStatistics")
    accesses = statistics.accesses
    return WritePolicyLaneStatisticsViewModel(
        lane_id=statistics.lane.lane_id,
        lane_label=statistics.lane.label,
        accesses=accesses,
        reads=statistics.reads,
        writes=statistics.writes,
        hits=statistics.hits,
        misses=statistics.misses,
        hit_rate=statistics.hits / accesses if accesses else 0.0,
        miss_rate=statistics.misses / accesses if accesses else 0.0,
        read_hits=statistics.read_hits,
        read_misses=statistics.read_misses,
        write_hits=statistics.write_hits,
        write_misses=statistics.write_misses,
        write_miss_allocations=statistics.write_miss_allocations,
        write_miss_bypasses=statistics.write_miss_bypasses,
        block_fills=statistics.block_fills,
        clean_evictions=statistics.clean_evictions,
        dirty_evictions=statistics.dirty_evictions,
        immediate_store_writes=statistics.immediate_store_writes,
        bypass_writes=statistics.bypass_writes,
        dirty_writebacks=statistics.dirty_writebacks,
        memory_read_transactions=statistics.memory_read_transactions,
        memory_read_bytes=statistics.memory_read_bytes,
        memory_write_transactions=statistics.memory_write_transactions,
        memory_write_bytes=statistics.memory_write_bytes,
        total_lower_memory_transactions=statistics.total_lower_memory_transactions,
        total_lower_memory_bytes=statistics.total_lower_memory_bytes,
        final_dirty_lines=statistics.final_dirty_lines,
        final_dirty_bytes=statistics.final_dirty_bytes,
        memory_write_bytes_with_final_drain=statistics.memory_write_bytes_with_final_drain,
        total_lower_memory_bytes_with_final_drain=statistics.total_lower_memory_bytes_with_final_drain,
        access_partition_ok=accesses == statistics.hits + statistics.misses
        == statistics.reads + statistics.writes,
        read_partition_ok=statistics.reads == statistics.read_hits + statistics.read_misses,
        write_partition_ok=statistics.writes == statistics.write_hits + statistics.write_misses,
        write_miss_partition_ok=(
            statistics.write_misses
            == statistics.write_miss_allocations + statistics.write_miss_bypasses
        ),
        fill_relation_ok=(
            statistics.block_fills
            == statistics.read_misses + statistics.write_miss_allocations
        ),
        dirty_writeback_relation_ok=(
            statistics.dirty_writebacks == statistics.dirty_evictions
        ),
        runtime_traffic_relation_ok=(
            statistics.total_lower_memory_transactions
            == statistics.memory_read_transactions + statistics.memory_write_transactions
            and statistics.total_lower_memory_bytes
            == statistics.memory_read_bytes + statistics.memory_write_bytes
        ),
        final_drain_relation_ok=(
            statistics.memory_write_bytes_with_final_drain
            == statistics.memory_write_bytes + statistics.final_dirty_bytes
            and statistics.total_lower_memory_bytes_with_final_drain
            == statistics.total_lower_memory_bytes + statistics.final_dirty_bytes
        ),
    )


__all__ = ["WritePolicyLaneStatisticsViewModel", "build_lane_statistics_view_model"]
