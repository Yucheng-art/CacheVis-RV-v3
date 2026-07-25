"""Pure display helpers for Cache Contents cards."""

from dataclasses import dataclass
from typing import Optional

from ..model import CacheLineViewModel


@dataclass(frozen=True)
class CacheLineCardViewModel:
    """Display model for one cache set/way card."""

    set_index: int
    way_index: int
    valid_text: str
    tag_text: str
    dirty_text: str
    last_used_text: str
    insert_time_text: str
    markers: tuple[str, ...]
    style_role: str
    tooltip: str


def build_cache_line_card_models(
    snapshot: list[list[CacheLineViewModel]],
    *,
    mapped_set: Optional[int],
    hit_way: Optional[int],
    victim_way: Optional[int],
    replacement_reason: Optional[str],
) -> list[list[CacheLineCardViewModel]]:
    """Build display cards from the current cache snapshot."""
    return [
        [
            build_cache_line_card_model(
                line,
                mapped_set=mapped_set,
                hit_way=hit_way,
                victim_way=victim_way,
                replacement_reason=replacement_reason,
            )
            for line in cache_set
        ]
        for cache_set in snapshot
    ]


def build_cache_line_card_model(
    line: CacheLineViewModel,
    *,
    mapped_set: Optional[int],
    hit_way: Optional[int],
    victim_way: Optional[int],
    replacement_reason: Optional[str],
) -> CacheLineCardViewModel:
    """Build one display card for a cache line."""
    markers: list[str] = []
    if mapped_set == line.set_index:
        markers.append("CURRENT SET")
    if mapped_set == line.set_index and hit_way == line.way_index:
        markers.append("HIT")
    if mapped_set == line.set_index and victim_way == line.way_index:
        if replacement_reason == "invalid-line":
            markers.append("INVALID FILL")
        else:
            markers.append("VICTIM")
    if not line.valid:
        markers.append("EMPTY")

    style_role = _style_role(tuple(markers))
    tag_text = format_tag(line.tag)
    last_used_text = _format_time(line.last_used, line.valid)
    insert_time_text = _format_time(line.insert_time, line.valid)
    tooltip = "\n".join(
        [
            f"set index: {line.set_index}",
            f"way index: {line.way_index}",
            f"valid: {int(line.valid)}",
            f"tag: {tag_text}",
            f"dirty: {int(line.dirty)}",
            f"last_used: {last_used_text}",
            f"insert_time: {insert_time_text}",
        ]
    )

    return CacheLineCardViewModel(
        set_index=line.set_index,
        way_index=line.way_index,
        valid_text=str(int(line.valid)),
        tag_text=tag_text,
        dirty_text=str(int(line.dirty)),
        last_used_text=last_used_text,
        insert_time_text=insert_time_text,
        markers=tuple(markers),
        style_role=style_role,
        tooltip=tooltip,
    )


def format_tag(tag: Optional[int]) -> str:
    """Format a cache tag for display."""
    if tag is None:
        return "-"
    return f"0x{tag:x}"


def _format_time(value: int, valid: bool) -> str:
    if not valid or value == 0:
        return "-"
    return str(value)


def _style_role(markers: tuple[str, ...]) -> str:
    if "HIT" in markers:
        return "hit"
    if "INVALID FILL" in markers:
        return "invalid_fill"
    if "VICTIM" in markers:
        return "victim"
    if "CURRENT SET" in markers:
        return "current_set"
    if "EMPTY" in markers:
        return "empty"
    return "normal"
