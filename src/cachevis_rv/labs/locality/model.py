"""Immutable domain models for cache-oriented locality analysis."""

from dataclasses import dataclass
from enum import Enum


class LocalityKind(str, Enum):
    """Mutually exclusive primary locality evidence for one access."""

    FIRST_TOUCH = "first_touch"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"


@dataclass(frozen=True)
class LocalityEvidence:
    """Trace-history evidence used to classify one address access."""

    address_seen_before: bool
    block_seen_before: bool
    offset_seen_before: bool
    previous_address_step: int | None
    previous_block_step: int | None
    address_reuse_gap: int | None
    block_reuse_gap: int | None
    block_reuse_distance: int | None
    same_block_as_previous: bool
    address_delta: int | None
    classification_reason: str

    def __post_init__(self) -> None:
        previous_steps = (
            self.previous_address_step,
            self.previous_block_step,
        )
        if any(value is not None and value < 0 for value in previous_steps):
            raise ValueError("previous step indexes must be non-negative or None")
        reuse_values = (
            self.address_reuse_gap,
            self.block_reuse_gap,
            self.block_reuse_distance,
        )
        if any(value is not None and value < 0 for value in reuse_values):
            raise ValueError("reuse gaps and distance must be non-negative or None")
        if self.address_seen_before != (self.previous_address_step is not None):
            raise ValueError("address history and previous_address_step disagree")
        if self.block_seen_before != (self.previous_block_step is not None):
            raise ValueError("block history and previous_block_step disagree")
        if self.address_seen_before != (self.address_reuse_gap is not None):
            raise ValueError("address reuse gap requires a previous address access")
        if self.block_seen_before != (self.block_reuse_gap is not None):
            raise ValueError("block reuse gap requires a previous block access")
        if self.block_seen_before != (self.block_reuse_distance is not None):
            raise ValueError("block reuse distance requires a previous block access")
        if not self.classification_reason:
            raise ValueError("classification_reason must not be empty")


@dataclass(frozen=True)
class LocalityStatistics:
    """Cumulative cache and locality statistics after an access."""

    accesses: int = 0
    hits: int = 0
    misses: int = 0
    unique_addresses: int = 0
    unique_blocks: int = 0
    first_touch_count: int = 0
    spatial_count: int = 0
    temporal_count: int = 0
    same_block_transition_count: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    spatial_event_rate: float = 0.0
    temporal_event_rate: float = 0.0
    average_address_reuse_gap: float | None = None
    average_block_reuse_gap: float | None = None
    average_block_reuse_distance: float | None = None

    def __post_init__(self) -> None:
        counts = (
            self.accesses,
            self.hits,
            self.misses,
            self.unique_addresses,
            self.unique_blocks,
            self.first_touch_count,
            self.spatial_count,
            self.temporal_count,
            self.same_block_transition_count,
        )
        if any(not isinstance(value, int) or value < 0 for value in counts):
            raise ValueError("statistics counts must be non-negative integers")
        if self.hits + self.misses != self.accesses:
            raise ValueError("hits + misses must equal accesses")
        if (
            self.first_touch_count + self.spatial_count + self.temporal_count
            != self.accesses
        ):
            raise ValueError("locality event counts must equal accesses")
        if self.first_touch_count != self.unique_blocks:
            raise ValueError("first touch count must equal unique blocks")
        if self.first_touch_count + self.spatial_count != self.unique_addresses:
            raise ValueError("first touch + spatial must equal unique addresses")
        rates = (
            self.hit_rate,
            self.miss_rate,
            self.spatial_event_rate,
            self.temporal_event_rate,
        )
        if any(not 0.0 <= value <= 1.0 for value in rates):
            raise ValueError("statistics rates must be between 0 and 1")
        averages = (
            self.average_address_reuse_gap,
            self.average_block_reuse_gap,
            self.average_block_reuse_distance,
        )
        if any(value is not None and value < 0.0 for value in averages):
            raise ValueError("reuse averages must be non-negative or None")


@dataclass(frozen=True)
class LocalityStep:
    """One cache access and its independent primary locality evidence."""

    step_index: int
    address: int
    block_address: int
    offset: int
    cache_result: str
    cache_hit: bool
    locality_kind: LocalityKind
    evidence: LocalityEvidence
    statistics: LocalityStatistics
    set_index: int | None = None
    hit_way: int | None = None
    victim_way: int | None = None
    invalid_fill: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.step_index, int) or self.step_index < 0:
            raise ValueError("step_index must be a non-negative integer")
        if not isinstance(self.address, int) or self.address < 0:
            raise ValueError("address must be a non-negative integer")
        if not isinstance(self.block_address, int) or self.block_address < 0:
            raise ValueError("block_address must be a non-negative integer")
        if not isinstance(self.offset, int) or self.offset < 0:
            raise ValueError("offset must be a non-negative integer")
        if self.cache_result not in {"hit", "miss"}:
            raise ValueError("cache_result must be 'hit' or 'miss'")
        if self.cache_hit != (self.cache_result == "hit"):
            raise ValueError("cache_hit and cache_result disagree")
        if not isinstance(self.locality_kind, LocalityKind):
            raise TypeError("locality_kind must be a LocalityKind")
        for name, value in (
            ("set_index", self.set_index),
            ("hit_way", self.hit_way),
            ("victim_way", self.victim_way),
        ):
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise ValueError(f"{name} must be a non-negative integer or None")
        marker_data_present = (
            self.set_index is not None
            or self.hit_way is not None
            or self.victim_way is not None
            or self.invalid_fill
        )
        if marker_data_present:
            if self.set_index is None:
                raise ValueError("cache marker data requires set_index")
            if self.cache_hit and self.hit_way is None:
                raise ValueError("a cache hit requires hit_way")
            if self.cache_hit and self.victim_way is not None:
                raise ValueError("a cache hit must not have victim_way")
            if not self.cache_hit and self.victim_way is None:
                raise ValueError("a cache miss requires victim_way")
            if not self.cache_hit and self.hit_way is not None:
                raise ValueError("a cache miss must not have hit_way")
            if self.invalid_fill and self.cache_hit:
                raise ValueError("invalid_fill applies only to cache misses")

    @property
    def address_hex(self) -> str:
        """Return a stable hexadecimal presentation of the address."""
        return f"0x{self.address:X}"


__all__ = [
    "LocalityKind",
    "LocalityEvidence",
    "LocalityStatistics",
    "LocalityStep",
]
