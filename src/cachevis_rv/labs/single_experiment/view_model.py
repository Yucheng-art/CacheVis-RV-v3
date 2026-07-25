"""Pure view model for the Single Experiment lab."""

from dataclasses import dataclass
from typing import Mapping

from cachevis_rv.core import CacheConfig


@dataclass(frozen=True)
class SingleExperimentViewModel:
    """Current result state rendered by the Single Experiment widget."""

    cache_config: CacheConfig | None
    summary: Mapping | None
    access_log: tuple[Mapping, ...]
    conclusion: str
    has_exportable_result: bool


EMPTY_SINGLE_EXPERIMENT_STATE = SingleExperimentViewModel(
    cache_config=None,
    summary=None,
    access_log=(),
    conclusion="",
    has_exportable_result=False,
)


__all__ = [
    "EMPTY_SINGLE_EXPERIMENT_STATE",
    "SingleExperimentViewModel",
]
