"""Synchronized actual/reference cache session for strict 3C classification."""

from collections.abc import Iterable

from cachevis_rv.core import CacheConfig, CacheSimulator

from .classifier import MissTypeClassifier
from .model import MissType, MissTypeStatistics, MissTypeStep


class MissTypeSession:
    """Run one LRU trace against actual and fully-associative reference caches."""

    def __init__(self, config: CacheConfig, addresses: Iterable[int]) -> None:
        if not isinstance(config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        if config.replacement_policy != "LRU":
            raise ValueError(
                "strict 3C classification requires an LRU actual cache"
            )

        self.config = config
        self.addresses = self._validate_addresses(addresses, config.address_bits)
        line_count = config.cache_size_bytes // config.block_size_bytes
        self.reference_config = CacheConfig(
            cache_size_bytes=config.cache_size_bytes,
            block_size_bytes=config.block_size_bytes,
            ways=line_count,
            replacement_policy="LRU",
            write_policy=config.write_policy,
            address_bits=config.address_bits,
        )
        self.actual_simulator = CacheSimulator(config)
        self.reference_simulator = CacheSimulator(self.reference_config)
        self.classifier = MissTypeClassifier()
        self._steps: list[MissTypeStep] = []
        self._next_step_index = 0
        self._statistics = MissTypeStatistics()

    @property
    def steps(self) -> tuple[MissTypeStep, ...]:
        """Return the completed steps as an immutable tuple."""
        return tuple(self._steps)

    @property
    def statistics(self) -> MissTypeStatistics:
        """Return current cumulative 3C statistics."""
        return self._statistics

    @property
    def is_complete(self) -> bool:
        """Return whether every address has been processed."""
        return self._next_step_index >= len(self.addresses)

    @property
    def next_step_index(self) -> int:
        """Return the zero-based index of the next address."""
        return self._next_step_index

    def reset(self) -> None:
        """Reset both caches, the classifier, steps, and statistics."""
        self.actual_simulator.reset()
        self.reference_simulator.reset()
        self.classifier.reset()
        self._steps.clear()
        self._next_step_index = 0
        self._statistics = MissTypeStatistics()

    def has_next(self) -> bool:
        """Return whether another trace address can be processed."""
        return not self.is_complete

    def step(self) -> MissTypeStep:
        """Process one synchronized actual/reference cache access."""
        if not self.has_next():
            raise StopIteration("miss type trace is complete")

        step_index = self._next_step_index
        address = self.addresses[step_index]
        block_address = address // self.config.block_size_bytes
        actual_access = self.actual_simulator.access(address)
        reference_access = self.reference_simulator.access(address)
        actual_hit = bool(actual_access["hit"])
        reference_hit = bool(reference_access["hit"])
        miss_type, evidence = self.classifier.classify(
            block_address,
            actual_hit=actual_hit,
            reference_hit=reference_hit,
        )
        statistics = self._next_statistics(actual_hit, miss_type)
        result = MissTypeStep(
            step_index=step_index,
            address=address,
            block_address=block_address,
            actual_result="hit" if actual_hit else "miss",
            reference_result="hit" if reference_hit else "miss",
            miss_type=miss_type,
            evidence=evidence,
            statistics=statistics,
        )
        self._steps.append(result)
        self._next_step_index += 1
        self._statistics = statistics
        return result

    def run_all(self) -> tuple[MissTypeStep, ...]:
        """Process all remaining addresses and return every completed step."""
        while self.has_next():
            self.step()
        return self.steps

    def _next_statistics(
        self,
        actual_hit: bool,
        miss_type: MissType | None,
    ) -> MissTypeStatistics:
        current = self._statistics
        accesses = current.accesses + 1
        hits = current.hits + int(actual_hit)
        misses = current.misses + int(not actual_hit)
        compulsory = current.compulsory_misses + int(
            miss_type is MissType.COMPULSORY
        )
        conflict = current.conflict_misses + int(
            miss_type is MissType.CONFLICT
        )
        capacity = current.capacity_misses + int(
            miss_type is MissType.CAPACITY
        )
        return MissTypeStatistics(
            accesses=accesses,
            hits=hits,
            misses=misses,
            compulsory_misses=compulsory,
            conflict_misses=conflict,
            capacity_misses=capacity,
            hit_rate=hits / accesses,
            miss_rate=misses / accesses,
        )

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


__all__ = ["MissTypeSession"]
