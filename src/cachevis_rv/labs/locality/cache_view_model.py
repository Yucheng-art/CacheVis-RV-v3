"""Immutable cache-line presentation models for Locality Lab."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .model import LocalityStep


@dataclass(frozen=True)
class LocalityCacheLineViewModel:
    """One detached cache line with markers for the current access."""

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


def build_cache_line_models(
    snapshot: Sequence[Sequence[Mapping[str, object]]],
    current_step: LocalityStep | None = None,
) -> tuple[LocalityCacheLineViewModel, ...]:
    """Convert a detached snapshot without rerunning any cache access."""
    set_index = current_step.set_index if current_step is not None else None
    hit_way = current_step.hit_way if current_step is not None else None
    victim_way = current_step.victim_way if current_step is not None else None
    invalid_fill = bool(current_step and current_step.invalid_fill)
    return tuple(
        LocalityCacheLineViewModel(
            set_index=int(line["set_index"]),
            way=int(line["way"]),
            valid=bool(line["valid"]),
            tag=None if line["tag"] is None else int(line["tag"]),
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


__all__ = ["LocalityCacheLineViewModel", "build_cache_line_models"]
