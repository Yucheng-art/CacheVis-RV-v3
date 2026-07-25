"""Small statistics helpers for cache simulation results."""


def hit_rate(hits: int, total_accesses: int) -> float:
    """Return hit rate as a float between 0.0 and 1.0."""
    if total_accesses <= 0:
        return 0.0
    return hits / total_accesses


def miss_rate(misses: int, total_accesses: int) -> float:
    """Return miss rate as a float between 0.0 and 1.0."""
    if total_accesses <= 0:
        return 0.0
    return misses / total_accesses


def summarize_results(total_accesses: int, hits: int, misses: int) -> dict:
    """Collect basic cache statistics into one summary dictionary."""
    return {
        "total_accesses": total_accesses,
        "hits": hits,
        "misses": misses,
        "hit_rate": hit_rate(hits, total_accesses),
        "miss_rate": miss_rate(misses, total_accesses),
    }
