"""Public cache simulation core."""

from .cache_config import CacheConfig
from .cache_line import CacheLine
from .cache_simulator import CacheSimulator
from .cache_statistics import hit_rate, miss_rate, summarize_results
from .replacement_policy import choose_victim_way

__all__ = [
    "CacheConfig",
    "CacheLine",
    "CacheSimulator",
    "choose_victim_way",
    "hit_rate",
    "miss_rate",
    "summarize_results",
]
