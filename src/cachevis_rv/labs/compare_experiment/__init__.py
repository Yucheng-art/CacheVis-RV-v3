"""Public comparison-experiment runner API."""

from .runner import build_comparison_configs, compare_cache_configs, run_comparison
from .controller import CompareExperimentController
from .view_model import CompareExperimentViewModel

__all__ = [
    "compare_cache_configs",
    "build_comparison_configs",
    "run_comparison",
    "CompareExperimentController",
    "CompareExperimentViewModel",
    "CompareExperimentWidget",
]


def __getattr__(name: str):
    if name == "CompareExperimentWidget":
        from .widget import CompareExperimentWidget

        return CompareExperimentWidget
    raise AttributeError(name)
