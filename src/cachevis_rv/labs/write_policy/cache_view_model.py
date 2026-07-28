"""Immutable cache snapshots suitable for later rendering."""

from dataclasses import dataclass

from .model import CacheSnapshot, WritePolicyLaneSpec


@dataclass(frozen=True)
class WritePolicyCacheLineViewModel:
    set_index: int
    way: int
    valid: bool
    tag: int | None
    tag_hex: str | None
    dirty: bool
    last_used: int
    insert_time: int
    state_label: str


@dataclass(frozen=True)
class WritePolicyLaneCacheViewModel:
    lane_id: str
    lane_label: str
    lines: tuple[WritePolicyCacheLineViewModel, ...]
    valid_line_count: int
    clean_line_count: int
    dirty_line_count: int
    dirty_bytes: int


def build_lane_cache_view_model(
    lane: WritePolicyLaneSpec, snapshot: CacheSnapshot, block_size_bytes: int
) -> WritePolicyLaneCacheViewModel:
    lines = tuple(
        WritePolicyCacheLineViewModel(
            set_index=line.set_index,
            way=line.way,
            valid=line.valid,
            tag=line.tag,
            tag_hex=None if line.tag is None else f"0x{line.tag:x}",
            dirty=line.dirty,
            last_used=line.last_used,
            insert_time=line.insert_time,
            state_label=("INVALID" if not line.valid else "DIRTY" if line.dirty else "CLEAN"),
        )
        for line in sorted(snapshot, key=lambda value: (value.set_index, value.way))
    )
    valid = sum(line.valid for line in lines)
    dirty = sum(line.valid and line.dirty for line in lines)
    return WritePolicyLaneCacheViewModel(
        lane_id=lane.lane_id,
        lane_label=lane.label,
        lines=lines,
        valid_line_count=valid,
        clean_line_count=valid - dirty,
        dirty_line_count=dirty,
        dirty_bytes=dirty * block_size_bytes,
    )


__all__ = [
    "WritePolicyCacheLineViewModel",
    "WritePolicyLaneCacheViewModel",
    "build_lane_cache_view_model",
]
