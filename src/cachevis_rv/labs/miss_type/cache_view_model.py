"""Immutable cache-line display models shared by actual and reference caches."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .model import MissTypeStep


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
    is_current_set: bool = False
    is_hit_way: bool = False
    is_victim_way: bool = False
    is_invalid_fill: bool = False

    def __post_init__(self) -> None:
        if self.cache_role not in CACHE_ROLES:
            raise ValueError("cache_role must be 'actual' or 'reference'")


def build_cache_line_models(
    snapshot: Sequence[Sequence[Mapping[str, object]]],
    cache_role: str,
    current_step: MissTypeStep | None = None,
) -> tuple[MissTypeCacheLineViewModel, ...]:
    """Convert one detached simulator snapshot into immutable line models."""
    if cache_role not in CACHE_ROLES:
        raise ValueError("cache_role must be 'actual' or 'reference'")

    set_index = _step_field(current_step, cache_role, "set_index")
    hit_way = _step_field(current_step, cache_role, "hit_way")
    victim_way = _step_field(current_step, cache_role, "victim_way")
    invalid_fill = bool(
        getattr(current_step, f"{cache_role}_invalid_fill", False)
    )

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
            is_current_set=(
                set_index is not None and int(line["set_index"]) == set_index
            ),
            is_hit_way=(
                hit_way is not None
                and int(line["set_index"]) == set_index
                and int(line["way"]) == hit_way
            ),
            is_victim_way=(
                victim_way is not None
                and int(line["set_index"]) == set_index
                and int(line["way"]) == victim_way
                and not invalid_fill
            ),
            is_invalid_fill=(
                victim_way is not None
                and int(line["set_index"]) == set_index
                and int(line["way"]) == victim_way
                and invalid_fill
            ),
        )
        for cache_set in snapshot
        for line in cache_set
    )


def _step_field(
    step: MissTypeStep | None,
    cache_role: str,
    suffix: str,
) -> int | None:
    if step is None:
        return None
    return getattr(step, f"{cache_role}_{suffix}")


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)


__all__ = [
    "CACHE_ROLES",
    "MissTypeCacheLineViewModel",
    "build_cache_line_models",
]
