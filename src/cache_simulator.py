"""Core cache simulator without GUI dependencies."""

from typing import Dict, List

from cache_config import CacheConfig
from cache_line import CacheLine
from replacement_policy import choose_victim_way
from statistics import hit_rate, summarize_results


class CacheSimulator:
    """Simulates set-associative cache accesses and basic statistics."""

    def __init__(self, config: CacheConfig | None = None) -> None:
        """Create an empty cache using the given configuration."""
        self.config = config if config is not None else CacheConfig()
        self._clock = 0
        self._access_id = 0
        self.total_accesses = 0
        self.hits = 0
        self.misses = 0
        self.cache: List[List[CacheLine]] = []
        self._create_empty_cache()

    def access(self, address: int, operation: str = "read") -> Dict[str, object]:
        """Access an address and return structured hit/miss information."""
        if operation not in {"read", "write"}:
            raise ValueError("operation must be 'read' or 'write'")

        parts = self.config.split_address(address)
        tag = parts["tag"]
        index = parts["index"]
        offset = parts["offset"]
        cache_set = self.cache[index]

        self._clock += 1
        self._access_id += 1
        self.total_accesses += 1

        hit_way = self._find_hit_way(cache_set, tag)
        hit = hit_way is not None
        victim_way = hit_way
        replaced_valid = False
        replaced_tag = None

        if hit:
            self.hits += 1
            line = cache_set[hit_way]
            line.last_used = self._clock
            if operation == "write" and self.config.write_policy != "write-through":
                line.dirty = True
        else:
            self.misses += 1
            victim_way = choose_victim_way(cache_set, self.config.replacement_policy)
            victim = cache_set[victim_way]
            replaced_valid = victim.valid
            replaced_tag = victim.tag

            victim.valid = True
            victim.tag = tag
            victim.dirty = operation == "write" and self.config.write_policy != "write-through"
            victim.last_used = self._clock
            victim.insert_time = self._clock

        return {
            "access_id": self._access_id,
            "address": address,
            "operation": operation,
            "tag": tag,
            "index": index,
            "offset": offset,
            "hit": hit,
            "victim_way": victim_way,
            "replaced_valid": replaced_valid,
            "replaced_tag": replaced_tag,
            "total_accesses": self.total_accesses,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate(self.hits, self.total_accesses),
        }

    def get_statistics(self) -> Dict[str, float | int]:
        """Return current aggregate cache statistics."""
        return summarize_results(self.total_accesses, self.hits, self.misses)

    def reset(self) -> None:
        """Clear cache contents and reset statistics."""
        self._clock = 0
        self._access_id = 0
        self.total_accesses = 0
        self.hits = 0
        self.misses = 0
        self._create_empty_cache()

    def get_cache_snapshot(self) -> List[List[Dict[str, int | bool | None]]]:
        """Return a table-friendly snapshot of all sets and ways."""
        return [
            [
                {
                    "set_index": set_index,
                    "way": way,
                    "valid": line.valid,
                    "tag": line.tag,
                    "dirty": line.dirty,
                    "last_used": line.last_used,
                    "insert_time": line.insert_time,
                }
                for way, line in enumerate(cache_set)
            ]
            for set_index, cache_set in enumerate(self.cache)
        ]

    def _create_empty_cache(self) -> None:
        self.cache = [
            [CacheLine() for _ in range(self.config.ways)]
            for _ in range(self.config.sets)
        ]

    @staticmethod
    def _find_hit_way(cache_set: List[CacheLine], tag: int) -> int | None:
        for way, line in enumerate(cache_set):
            if line.valid and line.tag == tag:
                return way
        return None
