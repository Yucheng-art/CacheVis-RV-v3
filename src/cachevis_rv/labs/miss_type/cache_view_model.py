"""Immutable cache-line display models shared by actual and reference caches."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


CACHE_ROLES = frozenset({"actual", "reference"})


@dataclass(frozen=True)
class MissTypeCacheLineViewModel:
    """One detached cache line suitable for later presentation."""

    cache_role: str
    set_index: int
    way: int
    valid: bool
    tag: int | None
    dirty: bool
    last_used: int
    insert_time: int

    def __post_init__(self) -> None:
        if self.cache_role not in CACHE_ROLES:
            raise ValueError("cache_role must be 'actual' or 'reference'")


def build_cache_line_models(
    snapshot: Sequence[Sequence[Mapping[str, object]]],
    cache_role: str,
) -> tuple[MissTypeCacheLineViewModel, ...]:
    """Convert one detached simulator snapshot into immutable line models."""
    if cache_role not in CACHE_ROLES:
        raise ValueError("cache_role must be 'actual' or 'reference'")

    return tuple(
        MissTypeCacheLineViewModel(
            cache_role=cache_role,
            set_index=int(line["set_index"]),
            way=int(line["way"]),
            valid=bool(line["valid"]),
            tag=_optional_int(line["tag"]),
            dirty=bool(line["dirty"]),
            last_used=int(line["last_used"]),
            insert_time=int(line["insert_time"]),
        )
        for cache_set in snapshot
        for line in cache_set
    )


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)


__all__ = [
    "CACHE_ROLES",
    "MissTypeCacheLineViewModel",
    "build_cache_line_models",
]
