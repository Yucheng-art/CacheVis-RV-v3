"""Compatibility facade for the packaged cache statistics helpers."""

from cachevis_rv.core.cache_statistics import hit_rate, miss_rate, summarize_results

__all__ = ["hit_rate", "miss_rate", "summarize_results"]
