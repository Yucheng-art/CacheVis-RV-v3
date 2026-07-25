"""Replacement policy helpers for selecting cache victim ways."""

import random
from typing import List, Optional

from cache_line import CacheLine


def choose_victim_way(
    lines: List[CacheLine],
    replacement_policy: str,
    random_source: Optional[random.Random] = None,
) -> int:
    """Choose a victim way, preferring invalid lines before policy logic."""
    if not lines:
        raise ValueError("lines must not be empty")

    for way, line in enumerate(lines):
        if not line.valid:
            return way

    if replacement_policy == "LRU":
        return min(range(len(lines)), key=lambda way: lines[way].last_used)
    if replacement_policy == "FIFO":
        return min(range(len(lines)), key=lambda way: lines[way].insert_time)
    if replacement_policy == "Random":
        source = random_source if random_source is not None else random
        return source.randrange(len(lines))

    raise ValueError(f"unsupported replacement policy: {replacement_policy}")
