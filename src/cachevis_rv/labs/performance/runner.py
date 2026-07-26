"""Cold-start execution through the official CacheSimulator."""

from collections.abc import Iterable

from cachevis_rv.core import CacheConfig, CacheSimulator

from .model import (
    PerformanceCacheLineSnapshot,
    PerformanceMetrics,
    PerformanceRunResult,
)
from .timing import PerformanceTimingModel


_RANDOM_REJECTION = (
    "Random performance ranking belongs to Policy Lab and is not "
    "deterministic in this core."
)


class PerformanceRunner:
    """Run one trace from an empty cache and apply explicit cycle assumptions."""

    def run(
        self,
        config: CacheConfig,
        addresses: Iterable[int],
        timing: PerformanceTimingModel,
    ) -> PerformanceRunResult:
        if not isinstance(config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        if not isinstance(timing, PerformanceTimingModel):
            raise TypeError("timing must be a PerformanceTimingModel")
        if config.replacement_policy == "Random":
            raise ValueError(_RANDOM_REJECTION)
        if config.replacement_policy not in {"LRU", "FIFO"}:
            raise ValueError("performance core supports only LRU and FIFO")

        stable_config = _copy_config(config)
        stable_addresses = _validate_addresses(addresses, stable_config.address_bits)
        simulator = CacheSimulator(stable_config)
        for address in stable_addresses:
            simulator.access(address)

        statistics = simulator.get_statistics()
        accesses = int(statistics["total_accesses"])
        hits = int(statistics["hits"])
        misses = int(statistics["misses"])
        hit_rate = float(statistics["hit_rate"])
        miss_rate = float(statistics["miss_rate"])
        penalty = timing.effective_miss_penalty(stable_config.block_size_bytes)
        lookup_cycles = accesses * timing.hit_time_cycles
        miss_penalty_cycles = misses * penalty
        total_cycles = lookup_cycles + miss_penalty_cycles
        bytes_fetched = misses * stable_config.block_size_bytes
        metrics = PerformanceMetrics(
            accesses=accesses,
            hits=hits,
            misses=misses,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            hit_time_cycles=timing.hit_time_cycles,
            effective_miss_penalty_cycles=penalty,
            total_lookup_cycles=lookup_cycles,
            total_miss_penalty_cycles=miss_penalty_cycles,
            total_cycles=total_cycles,
            amat_cycles=None if accesses == 0 else total_cycles / accesses,
            line_fills=misses,
            bytes_fetched=bytes_fetched,
            bytes_fetched_per_access=(
                None if accesses == 0 else bytes_fetched / accesses
            ),
            miss_stall_fraction=(
                None if total_cycles == 0.0 else miss_penalty_cycles / total_cycles
            ),
        )
        snapshot = tuple(
            tuple(
                PerformanceCacheLineSnapshot(
                    set_index=int(line["set_index"]),
                    way=int(line["way"]),
                    valid=bool(line["valid"]),
                    tag=None if line["tag"] is None else int(line["tag"]),
                    dirty=bool(line["dirty"]),
                    last_used=int(line["last_used"]),
                    insert_time=int(line["insert_time"]),
                )
                for line in cache_set
            )
            for cache_set in simulator.get_cache_snapshot()
        )
        return PerformanceRunResult(
            config=stable_config,
            timing=timing,
            addresses=stable_addresses,
            metrics=metrics,
            final_cache_snapshot=snapshot,
        )


def _copy_config(config: CacheConfig) -> CacheConfig:
    return CacheConfig(
        cache_size_bytes=config.cache_size_bytes,
        block_size_bytes=config.block_size_bytes,
        ways=config.ways,
        replacement_policy=config.replacement_policy,
        write_policy=config.write_policy,
        address_bits=config.address_bits,
    )


def _validate_addresses(addresses: Iterable[int], address_bits: int) -> tuple[int, ...]:
    if isinstance(addresses, (str, bytes)):
        raise TypeError("addresses must be an iterable of integers")
    try:
        stable = tuple(addresses)
    except TypeError as exc:
        raise TypeError("addresses must be an iterable of integers") from exc
    upper_bound = 1 << address_bits
    for address in stable:
        if isinstance(address, bool) or not isinstance(address, int):
            raise TypeError("every address must be an integer")
        if address < 0:
            raise ValueError("addresses must be non-negative")
        if address >= upper_bound:
            raise ValueError("address exceeds the configured address width")
    return stable


__all__ = ["PerformanceRunner"]
