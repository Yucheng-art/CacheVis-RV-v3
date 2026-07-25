"""Export cache experiment results to simple text formats."""

import csv
from pathlib import Path
from typing import Iterable, Mapping


ACCESS_LOG_FIELDS = [
    "access_id",
    "address",
    "operation",
    "tag",
    "index",
    "offset",
    "hit",
    "victim_way",
    "replaced_valid",
    "replaced_tag",
]

COMPARISON_FIELDS = [
    "config_name",
    "cache_size_bytes",
    "block_size_bytes",
    "ways",
    "replacement_policy",
    "total_accesses",
    "hits",
    "misses",
    "hit_rate",
    "miss_rate",
]


def export_access_log_csv(access_results: Iterable[Mapping], output_path) -> Path:
    """Write per-access simulation results to a CSV file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ACCESS_LOG_FIELDS)
        writer.writeheader()
        for result in access_results:
            writer.writerow({field: result.get(field) for field in ACCESS_LOG_FIELDS})

    return path


def export_markdown_report(
    output_path,
    *,
    software_name: str,
    software_version: str,
    experiment_name: str,
    cache_config,
    trace_type: str,
    summary: Mapping,
    conclusion: str,
) -> Path:
    """Write a compact Markdown report for one cache experiment."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {experiment_name}",
        "",
        f"- Software: {software_name}",
        f"- Version: {software_version}",
        f"- Trace type: {trace_type}",
        "",
        "## Cache Configuration",
        "",
        f"- Cache size: {cache_config.cache_size_bytes} bytes",
        f"- Block size: {cache_config.block_size_bytes} bytes",
        f"- Ways: {cache_config.ways}",
        f"- Sets: {cache_config.sets}",
        f"- Replacement policy: {cache_config.replacement_policy}",
        f"- Write policy: {cache_config.write_policy}",
        "",
        "## Statistics",
        "",
        f"- Total accesses: {summary['total_accesses']}",
        f"- Hits: {summary['hits']}",
        f"- Misses: {summary['misses']}",
        f"- Hit rate: {summary['hit_rate']:.2%}",
        f"- Miss rate: {summary['miss_rate']:.2%}",
        "",
        "## Conclusion",
        "",
        conclusion,
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def export_comparison_markdown_report(
    output_path,
    *,
    software_name: str,
    software_version: str,
    comparison_name: str,
    trace_type: str,
    trace_params: Mapping,
    summaries: Iterable[Mapping],
) -> Path:
    """Write a Markdown report for a multi-configuration comparison."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(summaries)

    lines = [
        f"# {comparison_name}",
        "",
        f"- Software: {software_name}",
        f"- Version: {software_version}",
        f"- Trace type: {trace_type}",
        f"- Trace params: {_format_params(trace_params)}",
        "",
        "## Comparison Table",
        "",
        "| Config | Cache size | Block size | Ways | Policy | Total | Hits | Misses | Hit rate | Miss rate |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in rows:
        lines.append(
            "| "
            f"{row.get('config_name', row.get('experiment_name', 'config'))} | "
            f"{row['cache_size_bytes']} | "
            f"{row['block_size_bytes']} | "
            f"{row['ways']} | "
            f"{row['replacement_policy']} | "
            f"{row['total_accesses']} | "
            f"{row['hits']} | "
            f"{row['misses']} | "
            f"{row['hit_rate']:.2%} | "
            f"{row['miss_rate']:.2%} |"
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            build_comparison_conclusion(rows),
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_comparison_conclusion(summaries: Iterable[Mapping]) -> str:
    """Create a short conclusion for comparison summaries."""
    rows = list(summaries)
    if not rows:
        return "No configurations were compared."

    best_hit_rate = max(row["hit_rate"] for row in rows)
    fewest_misses = min(row["misses"] for row in rows)
    best_hit_configs = [
        row.get("config_name", row.get("experiment_name", "config"))
        for row in rows
        if row["hit_rate"] == best_hit_rate
    ]
    fewest_miss_configs = [
        row.get("config_name", row.get("experiment_name", "config"))
        for row in rows
        if row["misses"] == fewest_misses
    ]

    if len(best_hit_configs) == len(rows) and len(fewest_miss_configs) == len(rows):
        return "All compared configurations produced the same result; this trace is not sensitive to the selected parameter."

    hit_label = "Tie for highest hit rate" if len(best_hit_configs) > 1 else "Highest hit rate"
    miss_label = "Tie for fewest misses" if len(fewest_miss_configs) > 1 else "Fewest misses"
    return (
        f"{hit_label}: {', '.join(best_hit_configs)} "
        f"({best_hit_rate:.2%}). {miss_label}: {', '.join(fewest_miss_configs)} "
        f"({fewest_misses})."
    )


def _format_params(params: Mapping) -> str:
    if not params:
        return "default"
    return ", ".join(f"{key}={value}" for key, value in sorted(params.items()))
