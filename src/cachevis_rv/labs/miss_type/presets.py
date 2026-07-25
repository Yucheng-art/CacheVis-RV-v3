"""Immutable pure-data presets for the strict 3C miss classifier."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .model import MissType


@dataclass(frozen=True)
class MissTypePreset:
    """One deterministic teaching trace and its expected miss classes."""

    name: str
    config: CacheConfig
    addresses: tuple[int, ...]
    expected: tuple[MissType, ...]


COMPULSORY_PRESET = MissTypePreset(
    name="Compulsory demo",
    config=CacheConfig(
        cache_size_bytes=4,
        block_size_bytes=1,
        ways=1,
        replacement_policy="LRU",
    ),
    addresses=(0, 1, 2, 3),
    expected=(
        MissType.COMPULSORY,
        MissType.COMPULSORY,
        MissType.COMPULSORY,
        MissType.COMPULSORY,
    ),
)

CONFLICT_PRESET = MissTypePreset(
    name="Conflict demo",
    config=CacheConfig(
        cache_size_bytes=4,
        block_size_bytes=1,
        ways=1,
        replacement_policy="LRU",
    ),
    addresses=(0, 4, 0, 4),
    expected=(
        MissType.COMPULSORY,
        MissType.COMPULSORY,
        MissType.CONFLICT,
        MissType.CONFLICT,
    ),
)

CAPACITY_PRESET = MissTypePreset(
    name="Capacity demo",
    config=CacheConfig(
        cache_size_bytes=2,
        block_size_bytes=1,
        ways=2,
        replacement_policy="LRU",
    ),
    addresses=(0, 1, 2, 0),
    expected=(
        MissType.COMPULSORY,
        MissType.COMPULSORY,
        MissType.COMPULSORY,
        MissType.CAPACITY,
    ),
)

MISS_TYPE_PRESETS = (
    COMPULSORY_PRESET,
    CONFLICT_PRESET,
    CAPACITY_PRESET,
)


__all__ = [
    "MissTypePreset",
    "COMPULSORY_PRESET",
    "CONFLICT_PRESET",
    "CAPACITY_PRESET",
    "MISS_TYPE_PRESETS",
]
