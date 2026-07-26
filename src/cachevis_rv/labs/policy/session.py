"""Synchronized comparison of official CacheSimulator policy lanes."""

from collections.abc import Iterable

from cachevis_rv.core import CacheConfig, CacheSimulator

from .explainer import POLICIES, PolicyDecisionExplainer
from .model import (
    PolicyComparisonStatistics,
    PolicyComparisonStep,
    PolicyDecisionKind,
    PolicyLaneStatistics,
    PolicyLaneStep,
    PolicyLineSnapshot,
)
from .random_stream import IsolatedRandomStream


CacheSnapshot = tuple[tuple[PolicyLineSnapshot, ...], ...]


class PolicyComparisonSession:
    """Execute the same trace independently through LRU/FIFO/Random lanes."""

    def __init__(
        self,
        config: CacheConfig,
        addresses: Iterable[int],
        random_seed: int = 2026,
    ) -> None:
        if not isinstance(config, CacheConfig):
            raise TypeError("config must be a CacheConfig")
        self.config = config
        self.addresses = self._validate_addresses(addresses, config.address_bits)
        self.policies = POLICIES
        self.random_seed = random_seed
        self._random_stream = IsolatedRandomStream(random_seed)
        self._simulators = {
            policy: CacheSimulator(self._policy_config(policy))
            for policy in self.policies
        }
        self._steps: list[PolicyComparisonStep] = []
        self._next_step_index = 0
        self._statistics = self._empty_statistics()

    @property
    def steps(self) -> tuple[PolicyComparisonStep, ...]:
        return tuple(self._steps)

    @property
    def statistics(self) -> PolicyComparisonStatistics:
        return self._statistics

    @property
    def is_complete(self) -> bool:
        return self._next_step_index >= len(self.addresses)

    @property
    def next_step_index(self) -> int:
        return self._next_step_index

    def reset(self) -> None:
        for simulator in self._simulators.values():
            simulator.reset()
        self._random_stream.reset()
        self._steps.clear()
        self._next_step_index = 0
        self._statistics = self._empty_statistics()

    def has_next(self) -> bool:
        return not self.is_complete

    def step(self) -> PolicyComparisonStep:
        if not self.has_next():
            raise StopIteration("policy comparison trace is complete")

        step_index = self._next_step_index
        address = self.addresses[step_index]
        parts = self.config.split_address(address)
        set_index = int(parts["index"])
        tag = int(parts["tag"])
        lane_steps: list[PolicyLaneStep] = []
        after_snapshots: list[CacheSnapshot] = []

        for policy in self.policies:
            before = self.get_cache_snapshot(policy)
            before_set = before[set_index]
            simulator = self._simulators[policy]
            random_index = (
                self._random_stream.draw_index if policy == "Random" else None
            )
            if policy == "Random":
                result = self._random_stream.run(
                    lambda simulator=simulator: simulator.access(address)
                )
            else:
                result = simulator.access(address)
            after = self.get_cache_snapshot(policy)
            after_set = after[set_index]
            evidence = PolicyDecisionExplainer.explain(
                policy,
                before_set,
                result,
                after_set,
                random_seed=self.random_seed,
                random_draw_index=random_index,
            )
            lane_steps.append(
                PolicyLaneStep(
                    policy=policy,
                    cache_result="hit" if bool(result["hit"]) else "miss",
                    cache_hit=bool(result["hit"]),
                    decision=evidence,
                    before_set_lines=before_set,
                    after_set_lines=after_set,
                )
            )
            after_snapshots.append(after)

        lanes = tuple(lane_steps)
        outcome_diverged = len({lane.cache_hit for lane in lanes}) > 1
        evictions = tuple(
            lane for lane in lanes
            if lane.decision.decision_kind is PolicyDecisionKind.EVICTION
        )
        victim_diverged = (
            len(evictions) >= 2
            and len({
                (lane.decision.victim_way, lane.decision.victim_tag)
                for lane in evictions
            }) > 1
        )
        state_diverged = len(set(after_snapshots)) > 1
        statistics = self._next_statistics(
            lanes, outcome_diverged, victim_diverged, state_diverged
        )
        comparison = PolicyComparisonStep(
            step_index=step_index,
            address=address,
            address_hex=f"0x{address:X}",
            block_address=address // self.config.block_size_bytes,
            set_index=set_index,
            tag=tag,
            lane_steps=lanes,
            outcome_diverged=outcome_diverged,
            victim_diverged=victim_diverged,
            state_diverged=state_diverged,
            statistics=statistics,
        )
        self._steps.append(comparison)
        self._next_step_index += 1
        self._statistics = statistics
        return comparison

    def run_all(self) -> tuple[PolicyComparisonStep, ...]:
        while self.has_next():
            self.step()
        return self.steps

    def get_cache_snapshot(self, policy: str) -> CacheSnapshot:
        if policy not in self.policies:
            raise ValueError(f"unsupported replacement policy: {policy}")
        raw = self._simulators[policy].get_cache_snapshot()
        return tuple(
            tuple(
                PolicyLineSnapshot(
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
            for cache_set in raw
        )

    def get_all_cache_snapshots(
        self,
    ) -> tuple[tuple[str, CacheSnapshot], ...]:
        return tuple(
            (policy, self.get_cache_snapshot(policy))
            for policy in self.policies
        )

    def _policy_config(self, policy: str) -> CacheConfig:
        return CacheConfig(
            cache_size_bytes=self.config.cache_size_bytes,
            block_size_bytes=self.config.block_size_bytes,
            ways=self.config.ways,
            replacement_policy=policy,
            write_policy=self.config.write_policy,
            address_bits=self.config.address_bits,
        )

    def _empty_statistics(self) -> PolicyComparisonStatistics:
        return PolicyComparisonStatistics(
            accesses=0,
            lane_statistics=tuple(
                PolicyLaneStatistics(policy=policy) for policy in self.policies
            ),
        )

    def _next_statistics(
        self,
        lane_steps: tuple[PolicyLaneStep, ...],
        outcome_diverged: bool,
        victim_diverged: bool,
        state_diverged: bool,
    ) -> PolicyComparisonStatistics:
        previous = {
            lane.policy: lane for lane in self._statistics.lane_statistics
        }
        lane_statistics = []
        for step in lane_steps:
            old = previous[step.policy]
            accesses = old.accesses + 1
            hits = old.hits + int(step.cache_hit)
            misses = old.misses + int(not step.cache_hit)
            invalid_fills = old.invalid_fills + int(
                step.decision.decision_kind is PolicyDecisionKind.INVALID_FILL
            )
            evictions = old.evictions + int(
                step.decision.decision_kind is PolicyDecisionKind.EVICTION
            )
            lane_statistics.append(
                PolicyLaneStatistics(
                    policy=step.policy,
                    accesses=accesses,
                    hits=hits,
                    misses=misses,
                    invalid_fills=invalid_fills,
                    evictions=evictions,
                    hit_rate=hits / accesses,
                    miss_rate=misses / accesses,
                )
            )
        accesses = self._statistics.accesses + 1
        return PolicyComparisonStatistics(
            accesses=accesses,
            lane_statistics=tuple(lane_statistics),
            all_agree_steps=(
                self._statistics.all_agree_steps + int(not outcome_diverged)
            ),
            outcome_divergence_steps=(
                self._statistics.outcome_divergence_steps
                + int(outcome_diverged)
            ),
            victim_divergence_steps=(
                self._statistics.victim_divergence_steps
                + int(victim_diverged)
            ),
            state_divergence_steps=(
                self._statistics.state_divergence_steps
                + int(state_diverged)
            ),
        )

    @staticmethod
    def _validate_addresses(
        addresses: Iterable[int], address_bits: int
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


__all__ = ["CacheSnapshot", "PolicyComparisonSession"]
