"""Reusable experiment runner for CacheVis-RV."""

from pathlib import Path
from typing import Mapping

from cachevis_rv.core import CacheConfig, CacheSimulator
from cachevis_rv.experiments import (
    generate_block_locality_trace,
    generate_conflict_trace,
    generate_loop_reuse_trace,
    generate_matrix_column_like_trace,
    generate_matrix_row_major_trace,
    generate_random_trace,
    generate_sequential_trace,
    generate_stride_trace,
)
from cachevis_rv.services import export_access_log_csv, export_markdown_report
from version import APP_NAME, APP_VERSION

SOFTWARE_NAME = APP_NAME
SOFTWARE_VERSION = APP_VERSION
DEFAULT_START_ADDRESS = 0x1000


def build_trace(trace_type: str, trace_params: Mapping | None = None) -> list[int]:
    """Build an address trace from a trace type and parameter dictionary."""
    params = dict(trace_params or {})
    count = params.get("count", 32)
    start_address = params.get("start_address", DEFAULT_START_ADDRESS)

    if trace_type == "sequential":
        return generate_sequential_trace(
            start_address, count, step=params.get("step", 4)
        )
    if trace_type == "stride":
        return generate_stride_trace(
            start_address, count, stride_bytes=params.get("stride_bytes", 64)
        )
    if trace_type == "random":
        return generate_random_trace(
            start_address,
            count,
            address_range_bytes=params.get("address_range_bytes", max(count * 16, 4)),
            alignment=params.get("alignment", 4),
            seed=params.get("seed", 1),
        )
    if trace_type == "matrix":
        return generate_matrix_row_major_trace(
            start_address, params.get("n", count), params.get("element_size", 4)
        )
    if trace_type == "conflict":
        return generate_conflict_trace(
            start_address,
            count,
            conflict_stride_bytes=params.get("conflict_stride_bytes", 4096),
            unique_blocks=params.get("unique_blocks", 4),
        )
    if trace_type == "loop-reuse":
        return generate_loop_reuse_trace(
            start_address,
            count,
            loop_size=params.get("loop_size", 4),
            step=params.get("step", 4),
        )
    if trace_type == "block-locality":
        return generate_block_locality_trace(
            start_address,
            count,
            block_size_bytes=params.get("block_size_bytes", 32),
            word_size=params.get("word_size", 4),
        )
    if trace_type == "matrix-row":
        return generate_matrix_row_major_trace(
            start_address, params.get("n", count), params.get("element_size", 4)
        )
    if trace_type == "matrix-column":
        return generate_matrix_column_like_trace(
            start_address, params.get("n", count), params.get("element_size", 4)
        )

    raise ValueError(f"unsupported trace type: {trace_type}")


def run_single_experiment(
    experiment_name: str,
    cache_config: CacheConfig,
    trace_type: str,
    trace_params: Mapping | None = None,
    export: bool = False,
    export_dir=None,
) -> dict:
    """Run one cache experiment and optionally export its results."""
    trace = build_trace(trace_type, trace_params)
    simulator = CacheSimulator(cache_config)
    access_results = [simulator.access(address) for address in trace]
    stats = simulator.get_statistics()

    summary = {
        "experiment_name": experiment_name,
        "trace_type": trace_type,
        "trace_params": dict(trace_params or {}),
        "cache_size_bytes": cache_config.cache_size_bytes,
        "block_size_bytes": cache_config.block_size_bytes,
        "ways": cache_config.ways,
        "replacement_policy": cache_config.replacement_policy,
        "write_policy": cache_config.write_policy,
        "sets": cache_config.sets,
        "total_accesses": stats["total_accesses"],
        "hits": stats["hits"],
        "misses": stats["misses"],
        "hit_rate": stats["hit_rate"],
        "miss_rate": stats["miss_rate"],
        "access_results": access_results,
    }

    if export:
        if export_dir is None:
            export_dir = "outputs"
        output_dir = Path(export_dir)
        safe_name = _safe_file_name(experiment_name)
        csv_path = output_dir / f"{safe_name}_access_log.csv"
        report_path = output_dir / f"{safe_name}_report.md"
        export_access_log_csv(access_results, csv_path)
        export_markdown_report(
            report_path,
            software_name=SOFTWARE_NAME,
            software_version=SOFTWARE_VERSION,
            experiment_name=experiment_name,
            cache_config=cache_config,
            trace_type=trace_type,
            summary=summary,
            conclusion=make_single_experiment_conclusion(summary),
        )
        summary["csv_path"] = str(csv_path)
        summary["report_path"] = str(report_path)

    return summary


def make_single_experiment_conclusion(summary: Mapping) -> str:
    """Create a short conclusion for one experiment."""
    if summary["total_accesses"] == 0:
        return "No memory accesses were generated, so cache behavior was not measured."
    if summary["hit_rate"] >= 0.8:
        return "The hit rate is high, showing strong locality for this trace."
    if summary["hit_rate"] >= 0.4:
        return "The hit rate is moderate; comparing more cache settings may be useful."
    return "The hit rate is low, suggesting frequent conflict or capacity misses."


def _safe_file_name(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
