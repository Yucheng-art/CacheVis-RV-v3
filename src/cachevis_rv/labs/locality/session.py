"""Synchronized cache execution and independent locality analysis."""

from collections.abc import Iterable
from types import MappingProxyType
from typing import Mapping

from cachevis_rv.core import CacheConfig, CacheSimulator

from .analyzer import LocalityAnalyzer
from .model import LocalityKind, LocalityStatistics, LocalityStep


class LocalitySession:
    """Execute one trace while preserving cache and locality evidence separately."""

    def __init__(self, config: CacheConfig, addresses: Iterable[int]) -> None:
        if not isinstance(config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        self.config = config
        self.addresses = self._validate_addresses(addresses, config.address_bits)
        self.cache_simulator = CacheSimulator(config)
        self.analyzer = LocalityAnalyzer()
        self._steps: list[LocalityStep] = []
        self._next_step_index = 0
        self._statistics = LocalityStatistics()
        self._address_reuse_gaps: list[int] = []
        self._block_reuse_gaps: list[int] = []
        self._block_reuse_distances: list[int] = []

    @property
    def steps(self) -> tuple[LocalityStep, ...]:
        return tuple(self._steps)

    @property
    def statistics(self) -> LocalityStatistics:
        return self._statistics

    @property
    def line_count(self) -> int:
        """Return the total number of cache lines."""
        return self.config.cache_size_bytes // self.config.block_size_bytes

    @property
    def is_complete(self) -> bool:
        return self._next_step_index >= len(self.addresses)

    @property
    def next_step_index(self) -> int:
        return self._next_step_index

    def reset(self) -> None:
        """Reset cache, analyzer, completed steps, samples, and counters."""
        self.cache_simulator.reset()
        self.analyzer.reset()
        self._steps.clear()
        self._next_step_index = 0
        self._statistics = LocalityStatistics()
        self._address_reuse_gaps.clear()
        self._block_reuse_gaps.clear()
        self._block_reuse_distances.clear()

    def has_next(self) -> bool:
        return not self.is_complete

    def step(self) -> LocalityStep:
        """Execute one cache access and attach independent locality evidence."""
        if not self.has_next():
            raise StopIteration("locality trace is complete")

        step_index = self._next_step_index
        address = self.addresses[step_index]
        locality_kind, evidence = self.analyzer.analyze(
            address,
            self.config.block_size_bytes,
            step_index,
        )
        cache_access = self.cache_simulator.access(address)
        cache_hit = bool(cache_access["hit"])
        statistics = self._next_statistics(cache_hit, locality_kind, evidence)
        result = LocalityStep(
            step_index=step_index,
            address=address,
            block_address=address // self.config.block_size_bytes,
            offset=address % self.config.block_size_bytes,
            cache_result="hit" if cache_hit else "miss",
            cache_hit=cache_hit,
            locality_kind=locality_kind,
            evidence=evidence,
            statistics=statistics,
            set_index=int(cache_access["index"]),
            hit_way=(
                int(cache_access["victim_way"]) if cache_hit else None
            ),
            victim_way=(
                None if cache_hit else int(cache_access["victim_way"])
            ),
            invalid_fill=(
                not cache_hit and not bool(cache_access["replaced_valid"])
            ),
        )
        self._steps.append(result)
        self._next_step_index += 1
        self._statistics = statistics
        return result

    def run_all(self) -> tuple[LocalityStep, ...]:
        while self.has_next():
            self.step()
        return self.steps

    def get_cache_snapshot(
        self,
    ) -> tuple[tuple[Mapping[str, object], ...], ...]:
        """Return an immutable, detached snapshot of the cache."""
        return tuple(
            tuple(MappingProxyType(dict(line)) for line in cache_set)
            for cache_set in self.cache_simulator.get_cache_snapshot()
        )

    def _next_statistics(
        self,
        cache_hit: bool,
        kind: LocalityKind,
        evidence,
    ) -> LocalityStatistics:
        if evidence.address_reuse_gap is not None:
            self._address_reuse_gaps.append(evidence.address_reuse_gap)
        if evidence.block_reuse_gap is not None:
            self._block_reuse_gaps.append(evidence.block_reuse_gap)
        if evidence.block_reuse_distance is not None:
            self._block_reuse_distances.append(evidence.block_reuse_distance)

        current = self._statistics
        accesses = current.accesses + 1
        hits = current.hits + int(cache_hit)
        misses = current.misses + int(not cache_hit)
        first_touch = current.first_touch_count + int(
            kind is LocalityKind.FIRST_TOUCH
        )
        spatial = current.spatial_count + int(kind is LocalityKind.SPATIAL)
        temporal = current.temporal_count + int(kind is LocalityKind.TEMPORAL)
        same_block = current.same_block_transition_count + int(
            evidence.same_block_as_previous
        )
        return LocalityStatistics(
            accesses=accesses,
            hits=hits,
            misses=misses,
            unique_addresses=len(self.analyzer.seen_addresses),
            unique_blocks=len(self.analyzer.seen_blocks),
            first_touch_count=first_touch,
            spatial_count=spatial,
            temporal_count=temporal,
            same_block_transition_count=same_block,
            hit_rate=hits / accesses,
            miss_rate=misses / accesses,
            spatial_event_rate=spatial / accesses,
            temporal_event_rate=temporal / accesses,
            average_address_reuse_gap=self._average(self._address_reuse_gaps),
            average_block_reuse_gap=self._average(self._block_reuse_gaps),
            average_block_reuse_distance=self._average(
                self._block_reuse_distances
            ),
        )

    @staticmethod
    def _average(values: list[int]) -> float | None:
        return sum(values) / len(values) if values else None

    @staticmethod
    def _validate_addresses(
        addresses: Iterable[int],
        address_bits: int,
    ) -> tuple[int, ...]:
        if isinstance(addresses, (str, bytes)):
            raise TypeError("addresses must be an iterable of integers")
        try:
            values = tuple(addresses)
        except TypeError as exc:
            raise TypeError("addresses must be an iterable of integers") from exc
        maximum = (1 << address_bits) - 1
        for address in values:
            if isinstance(address, bool) or not isinstance(address, int):
                raise TypeError("every address must be an integer")
            if address < 0:
                raise ValueError("addresses must be non-negative")
            if address > maximum:
                raise ValueError(
                    f"address {address} exceeds the {address_bits}-bit address range"
                )
        return values


__all__ = ["LocalitySession"]
