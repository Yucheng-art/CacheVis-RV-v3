"""Parameter comparison helpers for CacheVis-RV experiments."""

from pathlib import Path
from typing import Iterable, Mapping

from cache_config import CacheConfig
from experiment_runner import SOFTWARE_NAME, SOFTWARE_VERSION, run_single_experiment
from report_exporter import export_comparison_markdown_report


def compare_cache_configs(
    trace_type: str,
    trace_params: Mapping | None,
    configs: Iterable[tuple[str, CacheConfig] | CacheConfig],
) -> list[dict]:
    """Run the same trace against several cache configurations."""
    summaries = []
    for index, item in enumerate(configs, start=1):
        if isinstance(item, tuple):
            config_name, config = item
        else:
            config_name = f"config-{index}"
            config = item

        summary = run_single_experiment(
            config_name,
            config,
            trace_type,
            trace_params,
            export=False,
        )
        summary["config_name"] = config_name
        summary.pop("access_results", None)
        summaries.append(summary)
    return summaries


def build_comparison_configs(mode: str, base_config: CacheConfig) -> list[tuple[str, CacheConfig]]:
    """Build common teaching comparison configurations."""
    if mode == "ways":
        return [
            (
                f"{ways}-way",
                CacheConfig(
                    cache_size_bytes=base_config.cache_size_bytes,
                    block_size_bytes=base_config.block_size_bytes,
                    ways=ways,
                    replacement_policy=base_config.replacement_policy,
                    write_policy=base_config.write_policy,
                ),
            )
            for ways in (1, 2, 4)
        ]
    if mode == "block-size":
        return [
            (
                f"{block_size}B block",
                CacheConfig(
                    cache_size_bytes=base_config.cache_size_bytes,
                    block_size_bytes=block_size,
                    ways=base_config.ways,
                    replacement_policy=base_config.replacement_policy,
                    write_policy=base_config.write_policy,
                ),
            )
            for block_size in (16, 32, 64)
        ]
    if mode == "cache-size":
        return [
            (
                f"{cache_size // 1024}KB cache",
                CacheConfig(
                    cache_size_bytes=cache_size,
                    block_size_bytes=base_config.block_size_bytes,
                    ways=base_config.ways,
                    replacement_policy=base_config.replacement_policy,
                    write_policy=base_config.write_policy,
                ),
            )
            for cache_size in (4 * 1024, 8 * 1024, 16 * 1024)
        ]
    raise ValueError("mode must be one of: ways, block-size, cache-size")


def run_comparison(
    comparison_name: str,
    trace_type: str,
    trace_params: Mapping | None,
    configs: Iterable[tuple[str, CacheConfig] | CacheConfig],
    export: bool = False,
    export_dir=None,
) -> list[dict]:
    """Run a comparison and optionally export a Markdown report."""
    summaries = compare_cache_configs(trace_type, trace_params, configs)
    if export:
        if export_dir is None:
            export_dir = "outputs"
        output_path = Path(export_dir) / f"{_safe_file_name(comparison_name)}.md"
        export_comparison_markdown_report(
            output_path,
            software_name=SOFTWARE_NAME,
            software_version=SOFTWARE_VERSION,
            comparison_name=comparison_name,
            trace_type=trace_type,
            trace_params=dict(trace_params or {}),
            summaries=summaries,
        )
        for summary in summaries:
            summary["comparison_report_path"] = str(output_path)
    return summaries


def _safe_file_name(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
