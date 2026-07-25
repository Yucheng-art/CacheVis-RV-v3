"""Pure controller for the Compare Experiment lab."""

from pathlib import Path
from typing import Mapping

from cachevis_rv.core import CacheConfig
from cachevis_rv.services import (
    build_comparison_conclusion,
    export_comparison_markdown_report,
)

from .runner import build_comparison_configs, run_comparison
from .view_model import (
    EMPTY_COMPARE_EXPERIMENT_STATE,
    CompareExperimentViewModel,
)
from ..single_experiment.runner import SOFTWARE_NAME, SOFTWARE_VERSION


class CompareExperimentController:
    """Run, retain, clear, and export one classic parameter comparison."""

    def __init__(self) -> None:
        self._state = EMPTY_COMPARE_EXPERIMENT_STATE

    @property
    def state(self) -> CompareExperimentViewModel:
        return self._state

    def run(
        self,
        comparison_name: str,
        comparison_type: str,
        trace_type: str,
        trace_params: Mapping | None,
        base_config: CacheConfig,
    ) -> CompareExperimentViewModel:
        params = dict(trace_params or {})
        configs = build_comparison_configs(comparison_type, base_config)
        rows = run_comparison(
            comparison_name,
            trace_type,
            params,
            configs,
            export=False,
        )
        self._state = CompareExperimentViewModel(
            comparison_type=comparison_type,
            comparison_name=comparison_name,
            trace_type=trace_type,
            trace_params=params,
            rows=tuple(rows),
            conclusion=build_comparison_conclusion(rows),
            best_hit_rate=max((row["hit_rate"] for row in rows), default=0.0),
            has_exportable_result=bool(rows),
        )
        return self._state

    def clear(self) -> CompareExperimentViewModel:
        self._state = EMPTY_COMPARE_EXPERIMENT_STATE
        return self._state

    def export(self, output_dir) -> Path:
        state = self._state
        if not state.has_exportable_result or state.comparison_name is None:
            raise RuntimeError("please run a compare experiment first")
        if state.trace_type is None:
            raise RuntimeError("comparison trace type is unavailable")

        report_path = Path(output_dir) / (
            f"{_safe_file_name(state.comparison_name)}.md"
        )
        export_comparison_markdown_report(
            report_path,
            software_name=SOFTWARE_NAME,
            software_version=SOFTWARE_VERSION,
            comparison_name=state.comparison_name,
            trace_type=state.trace_type,
            trace_params=state.trace_params,
            summaries=state.rows,
        )
        return report_path


def _safe_file_name(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")


__all__ = ["CompareExperimentController"]
