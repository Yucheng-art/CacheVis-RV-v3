"""Pure view model for the Compare Experiment lab."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class CompareExperimentViewModel:
    """Current comparison state rendered by the Compare Experiment widget."""

    comparison_type: str | None
    comparison_name: str | None
    trace_type: str | None
    trace_params: Mapping
    rows: tuple[Mapping, ...]
    conclusion: str
    best_hit_rate: float
    has_exportable_result: bool


EMPTY_COMPARE_EXPERIMENT_STATE = CompareExperimentViewModel(
    comparison_type=None,
    comparison_name=None,
    trace_type=None,
    trace_params={},
    rows=(),
    conclusion="",
    best_hit_rate=0.0,
    has_exportable_result=False,
)


__all__ = [
    "CompareExperimentViewModel",
    "EMPTY_COMPARE_EXPERIMENT_STATE",
]
