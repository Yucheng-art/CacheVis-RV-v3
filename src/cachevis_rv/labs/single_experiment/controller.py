"""Pure controller for the Single Experiment lab."""

from pathlib import Path
from typing import Mapping

from cachevis_rv.core import CacheConfig
from cachevis_rv.services import export_access_log_csv, export_markdown_report

from .runner import (
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    make_single_experiment_conclusion,
    run_single_experiment,
)
from .view_model import (
    EMPTY_SINGLE_EXPERIMENT_STATE,
    SingleExperimentViewModel,
)


class SingleExperimentController:
    """Run, retain, clear, and export one classic cache experiment."""

    def __init__(self) -> None:
        self._state = EMPTY_SINGLE_EXPERIMENT_STATE

    @property
    def state(self) -> SingleExperimentViewModel:
        return self._state

    def run(
        self,
        experiment_name: str,
        cache_config: CacheConfig,
        trace_type: str,
        trace_params: Mapping | None = None,
    ) -> SingleExperimentViewModel:
        summary = run_single_experiment(
            experiment_name,
            cache_config,
            trace_type,
            trace_params,
            export=False,
        )
        conclusion = make_single_experiment_conclusion(summary)
        self._state = SingleExperimentViewModel(
            cache_config=cache_config,
            summary=summary,
            access_log=tuple(summary["access_results"]),
            conclusion=conclusion,
            has_exportable_result=True,
        )
        return self._state

    def clear(self) -> SingleExperimentViewModel:
        self._state = EMPTY_SINGLE_EXPERIMENT_STATE
        return self._state

    def export(self, output_dir) -> tuple[Path, Path]:
        state = self._state
        if not state.has_exportable_result or state.summary is None:
            raise RuntimeError("please run an experiment first")
        if state.cache_config is None:
            raise RuntimeError("cache configuration is unavailable")

        export_dir = Path(output_dir)
        safe_name = _safe_file_name(state.summary["experiment_name"])
        csv_path = export_dir / f"{safe_name}_access_log.csv"
        report_path = export_dir / f"{safe_name}_report.md"
        export_access_log_csv(state.access_log, csv_path)
        export_markdown_report(
            report_path,
            software_name=SOFTWARE_NAME,
            software_version=SOFTWARE_VERSION,
            experiment_name=state.summary["experiment_name"],
            cache_config=state.cache_config,
            trace_type=state.summary["trace_type"],
            summary=state.summary,
            conclusion=state.conclusion,
        )
        return csv_path, report_path


def _safe_file_name(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")


__all__ = ["SingleExperimentController"]
