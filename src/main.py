"""Command line entry point for CacheVis-RV experiments."""

import argparse
from pathlib import Path

from cache_config import CacheConfig
from compare_runner import build_comparison_configs, run_comparison
from experiment_runner import (
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    build_trace as build_runner_trace,
    run_single_experiment,
)


TRACE_TYPES = [
    "sequential",
    "stride",
    "random",
    "matrix",
    "conflict",
    "loop-reuse",
    "block-locality",
    "matrix-row",
    "matrix-column",
]


def non_negative_int(value: str) -> int:
    """Parse an argparse integer that must be zero or greater."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(description="Run a CacheVis-RV CLI experiment.")
    parser.add_argument(
        "--trace",
        choices=TRACE_TYPES,
        default="sequential",
        help="trace type to generate",
    )
    parser.add_argument(
        "--count",
        type=non_negative_int,
        default=32,
        help="number of accesses",
    )
    parser.add_argument(
        "--cache-size",
        type=int,
        default=8 * 1024,
        help="cache size in bytes",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=32,
        help="cache block size in bytes",
    )
    parser.add_argument("--ways", type=int, default=2, help="set associativity")
    parser.add_argument(
        "--policy",
        choices=["LRU", "FIFO", "Random"],
        default="LRU",
        help="replacement policy",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help="directory for CSV and Markdown exports",
    )
    parser.add_argument(
        "--compare",
        choices=["ways", "block-size", "cache-size"],
        default=None,
        help="run a parameter comparison instead of a single experiment",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="start the optional PySide6 desktop GUI",
    )
    return parser


def build_trace(trace_type: str, count: int) -> list[int]:
    """Build an address trace from a command line trace type."""
    return build_runner_trace(trace_type, {"count": count})


def run_experiment(config: CacheConfig, trace: list[int]) -> tuple[list[dict], dict]:
    """Run a direct trace for backward-compatible tests and callers."""
    from cache_simulator import CacheSimulator

    simulator = CacheSimulator(config)
    access_log = [simulator.access(address) for address in trace]
    return access_log, simulator.get_statistics()


def export_results(export_dir, trace_type, config, access_log, summary) -> tuple[Path, Path]:
    """Export single-experiment results for backward-compatible callers."""
    from report_exporter import export_access_log_csv, export_markdown_report

    output_dir = Path(export_dir)
    csv_path = output_dir / f"{trace_type}_access_log.csv"
    report_path = output_dir / f"{trace_type}_report.md"
    export_access_log_csv(access_log, csv_path)
    export_markdown_report(
        report_path,
        software_name=SOFTWARE_NAME,
        software_version=SOFTWARE_VERSION,
        experiment_name=f"{trace_type.title()} Trace Experiment",
        cache_config=config,
        trace_type=trace_type,
        summary=summary,
        conclusion=make_conclusion(summary),
    )
    return csv_path, report_path


def make_conclusion(summary: dict) -> str:
    """Create a short human-readable conclusion for the report."""
    if summary["total_accesses"] == 0:
        return "No memory accesses were generated, so cache behavior was not measured."
    if summary["hit_rate"] >= 0.8:
        return "The hit rate is high, showing strong locality for this trace."
    if summary["hit_rate"] >= 0.4:
        return "The hit rate is moderate; comparing more cache settings may be useful."
    return "The hit rate is low, suggesting frequent conflict or capacity misses."


def print_summary(trace_type: str, config: CacheConfig, summary: dict) -> None:
    """Print a compact command line summary."""
    print(f"{SOFTWARE_NAME} core simulator {SOFTWARE_VERSION}")
    print(
        "Config: "
        f"{config.cache_size_bytes}B cache, "
        f"{config.block_size_bytes}B block, "
        f"{config.ways}-way, "
        f"{config.replacement_policy}, "
        f"{config.write_policy}"
    )
    print(f"Trace: {trace_type}")
    print(f"Total accesses: {summary['total_accesses']}")
    print(f"Hits: {summary['hits']}")
    print(f"Misses: {summary['misses']}")
    print(f"Hit rate: {summary['hit_rate']:.2%}")
    print(f"Miss rate: {summary['miss_rate']:.2%}")


def print_comparison_table(summaries: list[dict]) -> None:
    """Print a compact comparison table."""
    print(f"{SOFTWARE_NAME} comparison {SOFTWARE_VERSION}")
    print("Config              Cache   Block  Ways  Policy  Total  Hits  Misses  Hit rate")
    print("-" * 82)
    for row in summaries:
        print(
            f"{row['config_name']:<18} "
            f"{row['cache_size_bytes']:>6} "
            f"{row['block_size_bytes']:>7} "
            f"{row['ways']:>5} "
            f"{row['replacement_policy']:<7} "
            f"{row['total_accesses']:>6} "
            f"{row['hits']:>5} "
            f"{row['misses']:>7} "
            f"{row['hit_rate']:>8.2%}"
        )


def main(argv=None) -> None:
    """Parse arguments, run an experiment, and optionally export results."""
    args = build_arg_parser().parse_args(argv)

    if args.gui:
        from gui_launcher import launch_gui

        exit_code = launch_gui()
        if exit_code:
            raise SystemExit(exit_code)
        return

    config = CacheConfig(
        cache_size_bytes=args.cache_size,
        block_size_bytes=args.block_size,
        ways=args.ways,
        replacement_policy=args.policy,
    )
    trace_params = {"count": args.count}

    if args.compare:
        configs = build_comparison_configs(args.compare, config)
        comparison_name = f"{args.compare} comparison on {args.trace} trace"
        summaries = run_comparison(
            comparison_name,
            args.trace,
            trace_params,
            configs,
            export=bool(args.export_dir),
            export_dir=args.export_dir,
        )
        print_comparison_table(summaries)
        if args.export_dir and summaries:
            print(f"Comparison report exported: {summaries[0]['comparison_report_path']}")
        return

    summary = run_single_experiment(
        f"{args.trace.title()} Trace Experiment",
        config,
        args.trace,
        trace_params,
        export=bool(args.export_dir),
        export_dir=args.export_dir,
    )
    print_summary(args.trace, config, summary)
    if args.export_dir:
        print(f"CSV exported: {summary['csv_path']}")
        print(f"Markdown report exported: {summary['report_path']}")


if __name__ == "__main__":
    main()
