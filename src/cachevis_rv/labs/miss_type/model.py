"""Immutable domain models for strict 3C cache-miss classification."""

from dataclasses import dataclass
from enum import Enum


class MissType(str, Enum):
    """The three miss classes in the foundational 3C model."""

    COMPULSORY = "compulsory"
    CONFLICT = "conflict"
    CAPACITY = "capacity"


@dataclass(frozen=True)
class MissTypeEvidence:
    """Evidence used to explain one hit or miss classification."""

    seen_before: bool
    actual_hit: bool
    reference_hit: bool
    actual_miss: bool
    reference_miss: bool
    classification_reason: str

    def __post_init__(self) -> None:
        if self.actual_hit == self.actual_miss:
            raise ValueError("actual evidence must describe exactly one of hit or miss")
        if self.reference_hit == self.reference_miss:
            raise ValueError("reference evidence must describe exactly one of hit or miss")
        if not self.classification_reason:
            raise ValueError("classification_reason must not be empty")


@dataclass(frozen=True)
class MissTypeStatistics:
    """Cumulative statistics after a classified access."""

    accesses: int = 0
    hits: int = 0
    misses: int = 0
    compulsory_misses: int = 0
    conflict_misses: int = 0
    capacity_misses: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0

    def __post_init__(self) -> None:
        counts = (
            self.accesses,
            self.hits,
            self.misses,
            self.compulsory_misses,
            self.conflict_misses,
            self.capacity_misses,
        )
        if any(not isinstance(value, int) or value < 0 for value in counts):
            raise ValueError("statistics counts must be non-negative integers")
        if self.hits + self.misses != self.accesses:
            raise ValueError("hits + misses must equal accesses")
        classified_misses = (
            self.compulsory_misses
            + self.conflict_misses
            + self.capacity_misses
        )
        if classified_misses != self.misses:
            raise ValueError("3C miss counts must equal misses")
        if not 0.0 <= self.hit_rate <= 1.0:
            raise ValueError("hit_rate must be between 0 and 1")
        if not 0.0 <= self.miss_rate <= 1.0:
            raise ValueError("miss_rate must be between 0 and 1")


@dataclass(frozen=True)
class MissTypeStep:
    """One actual/reference access pair and its cumulative result."""

    step_index: int
    address: int
    block_address: int
    actual_result: str
    reference_result: str
    miss_type: MissType | None
    evidence: MissTypeEvidence
    statistics: MissTypeStatistics
    actual_set_index: int | None = None
    actual_hit_way: int | None = None
    actual_victim_way: int | None = None
    reference_set_index: int | None = None
    reference_hit_way: int | None = None
    reference_victim_way: int | None = None
    actual_invalid_fill: bool = False
    reference_invalid_fill: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.step_index, int) or self.step_index < 0:
            raise ValueError("step_index must be a non-negative integer")
        if not isinstance(self.address, int) or self.address < 0:
            raise ValueError("address must be a non-negative integer")
        if not isinstance(self.block_address, int) or self.block_address < 0:
            raise ValueError("block_address must be a non-negative integer")
        if self.actual_result not in {"hit", "miss"}:
            raise ValueError("actual_result must be 'hit' or 'miss'")
        if self.reference_result not in {"hit", "miss"}:
            raise ValueError("reference_result must be 'hit' or 'miss'")
        if self.actual_result == "hit" and self.miss_type is not None:
            raise ValueError("a hit must not carry a miss type")
        if self.actual_result == "miss" and not isinstance(self.miss_type, MissType):
            raise ValueError("a miss must carry exactly one MissType")


__all__ = [
    "MissType",
    "MissTypeEvidence",
    "MissTypeStatistics",
    "MissTypeStep",
]
