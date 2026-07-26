"""Seven immutable teaching presets for write-policy comparison."""

from cachevis_rv.core import CacheConfig

from .model import WritePolicyPreset, WriteTrafficAssumptions
from .parser import parse_memory_access_trace


def _config(cache_size, block_size, ways):
    return CacheConfig(
        cache_size_bytes=cache_size,
        block_size_bytes=block_size,
        ways=ways,
        replacement_policy="LRU",
    )


def _summary(**values):
    return tuple(values.items())


def _lanes(wt_wa, wt_nwa, wb_wa, wb_nwa):
    return (
        ("wt_wa", wt_wa),
        ("wt_nwa", wt_nwa),
        ("wb_wa", wb_wa),
        ("wb_nwa", wb_nwa),
    )


WRITE_POLICY_PRESETS = (
    WritePolicyPreset(
        "read_only_control",
        "Read-Only Control",
        "A read-only trace isolates behavior that write policy must not change.",
        _config(32, 16, 2),
        parse_memory_access_trace("R 0, R 0, R 16, R 0"),
        WriteTrafficAssumptions(4),
        "Without writes, all four lanes have identical cache behavior and traffic.",
        _lanes(*(_summary(hits=2, misses=2, block_fills=2, memory_read_bytes=32,
                          memory_write_bytes=0, total_lower_memory_bytes=32,
                          final_dirty_bytes=0) for _ in range(4))),
    ),
    WritePolicyPreset(
        "repeated_resident_writes",
        "Repeated Writes to Resident Line",
        "Repeated writes distinguish immediate propagation from dirty aggregation.",
        _config(16, 16, 1),
        parse_memory_access_trace("R 0, W 0, W 0, W 0, W 0, W 0"),
        WriteTrafficAssumptions(4),
        "Allocation policy agrees on resident hits; write-back defers traffic but retains dirty data for eviction or drain.",
        _lanes(
            _summary(hits=5, misses=1, memory_read_bytes=16, memory_write_bytes=20,
                     total_lower_memory_bytes=36, final_dirty_bytes=0,
                     total_lower_memory_bytes_with_final_drain=36),
            _summary(hits=5, misses=1, memory_read_bytes=16, memory_write_bytes=20,
                     total_lower_memory_bytes=36, final_dirty_bytes=0,
                     total_lower_memory_bytes_with_final_drain=36),
            _summary(hits=5, misses=1, memory_read_bytes=16, memory_write_bytes=0,
                     total_lower_memory_bytes=16, final_dirty_bytes=16,
                     total_lower_memory_bytes_with_final_drain=32),
            _summary(hits=5, misses=1, memory_read_bytes=16, memory_write_bytes=0,
                     total_lower_memory_bytes=16, final_dirty_bytes=16,
                     total_lower_memory_bytes_with_final_drain=32),
        ),
    ),
    WritePolicyPreset(
        "allocate_vs_bypass",
        "Write Miss Allocate vs Bypass",
        "A read after a write miss exposes allocation-policy consequences.",
        _config(16, 16, 1),
        parse_memory_access_trace("W 0, R 0"),
        WriteTrafficAssumptions(4),
        "Write allocate enables the following read hit; bypass leaves that read as a miss.",
        _lanes(
            _summary(hits=1, misses=1, total_lower_memory_bytes=20),
            _summary(hits=0, misses=2, total_lower_memory_bytes=20),
            _summary(hits=1, misses=1, total_lower_memory_bytes=16,
                     final_dirty_bytes=16, total_lower_memory_bytes_with_final_drain=32),
            _summary(hits=0, misses=2, total_lower_memory_bytes=20,
                     final_dirty_bytes=0),
        ),
    ),
    WritePolicyPreset(
        "dirty_eviction",
        "Dirty Eviction",
        "Two conflicting stores expose whole-block dirty write-back traffic.",
        _config(16, 16, 1),
        parse_memory_access_trace("W 0, W 16"),
        WriteTrafficAssumptions(4),
        "A write-back dirty victim writes a whole block; write-through residents remain clean.",
        _lanes(
            _summary(block_fills=2, memory_read_bytes=32, memory_write_bytes=8,
                     total_lower_memory_bytes=40),
            _summary(block_fills=0, memory_write_bytes=8,
                     total_lower_memory_bytes=8),
            _summary(block_fills=2, memory_read_bytes=32, dirty_writebacks=1,
                     memory_write_bytes=16, total_lower_memory_bytes=48,
                     final_dirty_bytes=16, total_lower_memory_bytes_with_final_drain=64),
            _summary(block_fills=0, memory_write_bytes=8,
                     total_lower_memory_bytes=8),
        ),
    ),
    WritePolicyPreset(
        "streaming_stores",
        "Streaming Stores",
        "One-pass stores show the block-fill cost of allocation without reuse.",
        _config(16, 16, 1),
        parse_memory_access_trace("W 0, W 16, W 32, W 48"),
        WriteTrafficAssumptions(4),
        "For this no-reuse trace, bypass avoids block fills; this is not a claim that NWA is universally optimal.",
        _lanes(
            _summary(memory_read_bytes=64, memory_write_bytes=16,
                     total_lower_memory_bytes=80),
            _summary(memory_read_bytes=0, memory_write_bytes=16,
                     total_lower_memory_bytes=16),
            _summary(memory_read_bytes=64, memory_write_bytes=48,
                     total_lower_memory_bytes=112, final_dirty_bytes=16,
                     total_lower_memory_bytes_with_final_drain=128),
            _summary(memory_read_bytes=0, memory_write_bytes=16,
                     total_lower_memory_bytes=16),
        ),
    ),
    WritePolicyPreset(
        "read_after_write_reuse",
        "Read-After-Write Reuse",
        "Repeated reads reveal whether a write miss populated the cache.",
        _config(16, 16, 1),
        parse_memory_access_trace("W 0, R 0, R 0"),
        WriteTrafficAssumptions(4),
        "Write allocate preserves the written block for later read reuse; bypass does not prefill it.",
        _lanes(
            _summary(hits=2, misses=1, total_lower_memory_bytes=20),
            _summary(hits=1, misses=2, total_lower_memory_bytes=20),
            _summary(hits=2, misses=1, total_lower_memory_bytes=16,
                     final_dirty_bytes=16, total_lower_memory_bytes_with_final_drain=32),
            _summary(hits=1, misses=2, total_lower_memory_bytes=20),
        ),
    ),
    WritePolicyPreset(
        "mixed_dirty_conflict",
        "Mixed Dirty Conflict",
        "A mixed trace combines outcome, cache-state, dirty-state, and traffic divergence.",
        _config(32, 16, 2),
        parse_memory_access_trace("W 0, W 16, R 0, W 32, R 16"),
        WriteTrafficAssumptions(4),
        "Allocation changes future hits while propagation changes dirty state and eviction traffic.",
        _lanes(
            _summary(hits=1, misses=4, block_fills=4, memory_read_bytes=64,
                     memory_write_bytes=12, total_lower_memory_bytes=76),
            _summary(hits=0, misses=5, block_fills=2, memory_read_bytes=32,
                     memory_write_bytes=12, total_lower_memory_bytes=44),
            _summary(hits=1, misses=4, block_fills=4, memory_read_bytes=64,
                     dirty_writebacks=2, memory_write_bytes=32,
                     total_lower_memory_bytes=96, final_dirty_bytes=16,
                     total_lower_memory_bytes_with_final_drain=112),
            _summary(hits=0, misses=5, block_fills=2, memory_read_bytes=32,
                     memory_write_bytes=12, total_lower_memory_bytes=44),
        ),
    ),
)


def get_write_policy_preset(preset_id: str) -> WritePolicyPreset:
    for preset in WRITE_POLICY_PRESETS:
        if preset.preset_id == preset_id:
            return preset
    raise ValueError(f"unknown write-policy preset: {preset_id}")


__all__ = ["WRITE_POLICY_PRESETS", "get_write_policy_preset"]
