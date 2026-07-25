"""View models for the Address & Cache Visualizer logic layer."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CacheLineViewModel:
    """Serializable cache line state for one set/way position."""

    set_index: int
    way_index: int
    valid: bool
    tag: Optional[int]
    dirty: bool
    last_used: int
    insert_time: int


@dataclass(frozen=True)
class AccessStepViewModel:
    """Complete data needed to render and explain one stepped access."""

    step_index: int
    address: int
    address_dec: str
    address_hex: str
    address_binary: str
    tag_bits: int
    index_bits: int
    offset_bits: int
    tag: int
    index: int
    offset: int
    mapped_set: int
    hit: bool
    hit_way: Optional[int]
    victim_way: Optional[int]
    replaced_valid: bool
    replaced_tag: Optional[int]
    replacement_reason: Optional[str]
    miss_type: Optional[str]
    before_set_lines: list[CacheLineViewModel]
    after_cache_snapshot: list[list[CacheLineViewModel]]
    total_accesses: int
    hits: int
    misses: int
    hit_rate: float
    miss_rate: float
    explanation_lines: list[str]
