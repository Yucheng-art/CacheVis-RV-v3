"""Immutable domain models for write-policy traffic analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class MemoryAccessKind(Enum):
    READ = "read"
    WRITE = "write"


@dataclass(frozen=True)
class MemoryAccess:
    kind: MemoryAccessKind
    address: int

    def __post_init__(self) -> None:
        if not isinstance(self.kind, MemoryAccessKind):
            raise ValueError("kind must be a MemoryAccessKind")
        if isinstance(self.address, bool) or not isinstance(self.address, int):
            raise ValueError("address must be an integer")
        if self.address < 0:
            raise ValueError("address must be non-negative")


@dataclass(frozen=True)
class WriteTrafficAssumptions:
    store_size_bytes: int = 4

    def __post_init__(self) -> None:
        if isinstance(self.store_size_bytes, bool) or not isinstance(
            self.store_size_bytes, int
        ):
            raise ValueError("store_size_bytes must be an integer")
        if self.store_size_bytes <= 0:
            raise ValueError("store_size_bytes must be positive")


@dataclass(frozen=True)
class WritePolicyLaneSpec:
    lane_id: str
    label: str
    write_policy: str
    write_allocate: bool

    def __post_init__(self) -> None:
        if self.write_policy not in {"write-through", "write-back"}:
            raise ValueError("write_policy must be 'write-through' or 'write-back'")
        if not isinstance(self.write_allocate, bool):
            raise ValueError("write_allocate must be a bool")


WRITE_POLICY_LANES = (
    WritePolicyLaneSpec("wt_wa", "WT + WA", "write-through", True),
    WritePolicyLaneSpec("wt_nwa", "WT + NWA", "write-through", False),
    WritePolicyLaneSpec("wb_wa", "WB + WA", "write-back", True),
    WritePolicyLaneSpec("wb_nwa", "WB + NWA", "write-back", False),
)


class WriteDecisionKind(Enum):
    READ_HIT = "read-hit"
    READ_MISS_FILL = "read-miss-fill"
    WRITE_HIT_THROUGH = "write-hit-through"
    WRITE_HIT_BACK = "write-hit-back"
    WRITE_MISS_ALLOCATE_THROUGH = "write-miss-allocate-through"
    WRITE_MISS_ALLOCATE_BACK = "write-miss-allocate-back"
    WRITE_MISS_BYPASS = "write-miss-bypass"


@dataclass(frozen=True)
class WritePolicyLineSnapshot:
    set_index: int
    way: int
    valid: bool
    tag: int | None
    dirty: bool
    last_used: int
    insert_time: int


CacheSnapshot = tuple[WritePolicyLineSnapshot, ...]


@dataclass(frozen=True)
class WriteTrafficDelta:
    block_fills: int = 0
    block_fill_bytes: int = 0
    immediate_store_writes: int = 0
    immediate_store_bytes: int = 0
    bypass_writes: int = 0
    bypass_write_bytes: int = 0
    dirty_writebacks: int = 0
    dirty_writeback_bytes: int = 0
    memory_read_transactions: int = 0
    memory_read_bytes: int = 0
    memory_write_transactions: int = 0
    memory_write_bytes: int = 0
    total_lower_memory_transactions: int = 0
    total_lower_memory_bytes: int = 0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")


@dataclass(frozen=True)
class WritePolicyDecisionEvidence:
    lane: WritePolicyLaneSpec
    access: MemoryAccess
    decision_kind: WriteDecisionKind
    block_address: int
    set_index: int
    tag: int
    cache_hit: bool
    allocated: bool
    bypassed: bool
    hit_way: int | None
    fill_way: int | None
    evicted_way: int | None
    victim_tag: int | None
    victim_dirty: bool
    line_dirty_before: bool | None
    line_dirty_after: bool | None
    before_set_lines: tuple[WritePolicyLineSnapshot, ...]
    after_set_lines: tuple[WritePolicyLineSnapshot, ...]
    traffic_delta: WriteTrafficDelta
    classification_reason: str
    rule_path: tuple[str, ...]
    metadata_consistent: bool


@dataclass(frozen=True)
class WritePolicyLaneStep:
    lane: WritePolicyLaneSpec
    access_result: Mapping[str, object]
    evidence: WritePolicyDecisionEvidence
    before_cache_snapshot: CacheSnapshot
    after_cache_snapshot: CacheSnapshot


@dataclass(frozen=True)
class WritePolicyLaneStatistics:
    lane: WritePolicyLaneSpec
    accesses: int = 0
    reads: int = 0
    writes: int = 0
    hits: int = 0
    misses: int = 0
    read_hits: int = 0
    read_misses: int = 0
    write_hits: int = 0
    write_misses: int = 0
    write_miss_allocations: int = 0
    write_miss_bypasses: int = 0
    block_fills: int = 0
    clean_evictions: int = 0
    dirty_evictions: int = 0
    immediate_store_writes: int = 0
    bypass_writes: int = 0
    dirty_writebacks: int = 0
    memory_read_transactions: int = 0
    memory_read_bytes: int = 0
    memory_write_transactions: int = 0
    memory_write_bytes: int = 0
    total_lower_memory_transactions: int = 0
    total_lower_memory_bytes: int = 0
    final_dirty_lines: int = 0
    final_dirty_bytes: int = 0
    memory_write_bytes_with_final_drain: int = 0
    total_lower_memory_bytes_with_final_drain: int = 0


@dataclass(frozen=True)
class WritePolicyComparisonStatistics:
    accesses: int
    lane_statistics: tuple[WritePolicyLaneStatistics, ...]
    all_outcomes_agree_steps: int
    outcome_divergence_steps: int
    allocation_divergence_steps: int
    bypass_divergence_steps: int
    writeback_divergence_steps: int
    traffic_divergence_steps: int
    dirty_state_divergence_steps: int
    cache_state_divergence_steps: int


@dataclass(frozen=True)
class WritePolicyComparisonStep:
    step_index: int
    access: MemoryAccess
    address_hex: str
    block_address: int
    set_index: int
    tag: int
    lane_steps: tuple[WritePolicyLaneStep, ...]
    outcome_diverged: bool
    allocation_diverged: bool
    bypass_diverged: bool
    writeback_diverged: bool
    traffic_diverged: bool
    dirty_state_diverged: bool
    cache_state_diverged: bool
    statistics: WritePolicyComparisonStatistics


@dataclass(frozen=True)
class WritePolicyPreset:
    preset_id: str
    title: str
    description: str
    config: object
    accesses: tuple[MemoryAccess, ...]
    assumptions: WriteTrafficAssumptions
    expected_teaching_conclusion: str
    expected_lane_summary: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
