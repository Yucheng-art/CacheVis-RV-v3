"""Compatibility facade for the packaged comparison-experiment runner."""

from cachevis_rv.labs.compare_experiment.runner import (
    build_comparison_configs,
    compare_cache_configs,
    run_comparison,
)

__all__ = [
    "compare_cache_configs",
    "build_comparison_configs",
    "run_comparison",
]
