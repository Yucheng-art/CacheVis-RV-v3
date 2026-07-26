"""Four-lane write-policy comparison driven by independent core simulators."""

from dataclasses import replace
from types import MappingProxyType

from cachevis_rv.core import CacheConfig, CacheSimulator

from .explainer import WritePolicyExplainer, snapshot_cache
from .model import (
    CacheSnapshot,
    MemoryAccess,
    MemoryAccessKind,
    WRITE_POLICY_LANES,
    WritePolicyComparisonStatistics,
    WritePolicyComparisonStep,
    WritePolicyLaneStatistics,
    WritePolicyLaneStep,
    WriteTrafficAssumptions,
)


class WritePolicyComparisonSession:
    def __init__(
        self,
        config: CacheConfig,
        accesses: tuple[MemoryAccess, ...],
        assumptions: WriteTrafficAssumptions,
    ) -> None:
        if not isinstance(config, CacheConfig):
            raise ValueError("config must be a CacheConfig")
        if not isinstance(assumptions, WriteTrafficAssumptions):
            raise ValueError("assumptions must be WriteTrafficAssumptions")
        self.config = config
        self.accesses = tuple(accesses)
        self.assumptions = assumptions
        self._validate_inputs()
        self.reset()

    @property
    def lanes(self):
        return WRITE_POLICY_LANES

    @property
    def steps(self) -> tuple[WritePolicyComparisonStep, ...]:
        return tuple(self._steps)

    @property
    def is_complete(self) -> bool:
        return self._next_step_index >= len(self.accesses)

    @property
    def next_step_index(self) -> int:
        return self._next_step_index

    @property
    def statistics(self) -> WritePolicyComparisonStatistics:
        return self._build_statistics()

    def reset(self) -> None:
        self._simulators = {
            lane.lane_id: CacheSimulator(
                replace(
                    self.config,
                    write_policy=lane.write_policy,
                    write_allocate=lane.write_allocate,
                )
            )
            for lane in WRITE_POLICY_LANES
        }
        self._steps: list[WritePolicyComparisonStep] = []
        self._next_step_index = 0

    def has_next(self) -> bool:
        return not self.is_complete

    def step(self) -> WritePolicyComparisonStep:
        if self.is_complete:
            raise StopIteration("write-policy trace is complete")
        access = self.accesses[self._next_step_index]
        lane_steps = []
        for lane in WRITE_POLICY_LANES:
            simulator = self._simulators[lane.lane_id]
            before = snapshot_cache(simulator.get_cache_snapshot())
            result = simulator.access(access.address, access.kind.value)
            after = snapshot_cache(simulator.get_cache_snapshot())
            evidence = WritePolicyExplainer.explain(
                lane,
                access,
                self.assumptions,
                simulator.config,
                before,
                result,
                after,
            )
            lane_steps.append(
                WritePolicyLaneStep(
                    lane=lane,
                    access_result=MappingProxyType(dict(result)),
                    evidence=evidence,
                    before_cache_snapshot=before,
                    after_cache_snapshot=after,
                )
            )
        lane_steps_tuple = tuple(lane_steps)
        divergences = _divergences(lane_steps_tuple)
        statistics = self._build_statistics(lane_steps_tuple, divergences)
        parts = self.config.split_address(access.address)
        comparison_step = WritePolicyComparisonStep(
            step_index=self._next_step_index,
            access=access,
            address_hex=f"0x{access.address:x}",
            block_address=access.address // self.config.block_size_bytes,
            set_index=parts["index"],
            tag=parts["tag"],
            lane_steps=lane_steps_tuple,
            outcome_diverged=divergences[0],
            allocation_diverged=divergences[1],
            bypass_diverged=divergences[2],
            writeback_diverged=divergences[3],
            traffic_diverged=divergences[4],
            dirty_state_diverged=divergences[5],
            cache_state_diverged=divergences[6],
            statistics=statistics,
        )
        self._steps.append(comparison_step)
        self._next_step_index += 1
        return comparison_step

    def run_all(self) -> tuple[WritePolicyComparisonStep, ...]:
        while self.has_next():
            self.step()
        return self.steps

    def get_cache_snapshot(self, lane_id: str) -> CacheSnapshot:
        try:
            simulator = self._simulators[lane_id]
        except KeyError as exc:
            raise ValueError(f"unknown write-policy lane: {lane_id}") from exc
        return snapshot_cache(simulator.get_cache_snapshot())

    def get_all_cache_snapshots(self):
        return tuple(
            (lane.lane_id, self.get_cache_snapshot(lane.lane_id))
            for lane in WRITE_POLICY_LANES
        )

    def _validate_inputs(self) -> None:
        if self.assumptions.store_size_bytes > self.config.block_size_bytes:
            raise ValueError("store_size_bytes must not exceed block_size_bytes")
        max_address = (1 << self.config.address_bits) - 1
        for access in self.accesses:
            if not isinstance(access, MemoryAccess):
                raise ValueError("accesses must contain MemoryAccess values")
            if access.address > max_address:
                raise ValueError("address exceeds configured address width")
            if access.kind is MemoryAccessKind.WRITE:
                offset = access.address & self.config.offset_mask
                if offset + self.assumptions.store_size_bytes > self.config.block_size_bytes:
                    raise ValueError("write access crosses a cache-block boundary")

    def _build_statistics(self, current_lane_steps=(), current_divergences=None):
        all_lane_steps = [list() for _ in WRITE_POLICY_LANES]
        for comparison_step in self._steps:
            for index, lane_step in enumerate(comparison_step.lane_steps):
                all_lane_steps[index].append(lane_step)
        for index, lane_step in enumerate(current_lane_steps):
            all_lane_steps[index].append(lane_step)

        lane_statistics = tuple(
            self._lane_statistics(lane, tuple(all_lane_steps[index]))
            for index, lane in enumerate(WRITE_POLICY_LANES)
        )
        flags = [
            (
                step.outcome_diverged,
                step.allocation_diverged,
                step.bypass_diverged,
                step.writeback_diverged,
                step.traffic_diverged,
                step.dirty_state_diverged,
                step.cache_state_diverged,
            )
            for step in self._steps
        ]
        if current_divergences is not None:
            flags.append(current_divergences)
        accesses = len(flags)
        return WritePolicyComparisonStatistics(
            accesses=accesses,
            lane_statistics=lane_statistics,
            all_outcomes_agree_steps=sum(not flag[0] for flag in flags),
            outcome_divergence_steps=sum(flag[0] for flag in flags),
            allocation_divergence_steps=sum(flag[1] for flag in flags),
            bypass_divergence_steps=sum(flag[2] for flag in flags),
            writeback_divergence_steps=sum(flag[3] for flag in flags),
            traffic_divergence_steps=sum(flag[4] for flag in flags),
            dirty_state_divergence_steps=sum(flag[5] for flag in flags),
            cache_state_divergence_steps=sum(flag[6] for flag in flags),
        )

    def _lane_statistics(self, lane, lane_steps):
        accesses = len(lane_steps)
        reads = sum(step.evidence.access.kind is MemoryAccessKind.READ for step in lane_steps)
        hits = sum(step.evidence.cache_hit for step in lane_steps)
        read_hits = sum(
            step.evidence.access.kind is MemoryAccessKind.READ and step.evidence.cache_hit
            for step in lane_steps
        )
        write_hits = sum(
            step.evidence.access.kind is MemoryAccessKind.WRITE and step.evidence.cache_hit
            for step in lane_steps
        )
        writes = accesses - reads
        read_misses = reads - read_hits
        write_misses = writes - write_hits
        write_allocations = sum(
            step.evidence.access.kind is MemoryAccessKind.WRITE
            and not step.evidence.cache_hit
            and step.evidence.allocated
            for step in lane_steps
        )
        write_bypasses = sum(
            step.evidence.access.kind is MemoryAccessKind.WRITE
            and step.evidence.bypassed
            for step in lane_steps
        )
        traffic = tuple(step.evidence.traffic_delta for step in lane_steps)
        clean_evictions = sum(
            step.evidence.evicted_way is not None and not step.evidence.victim_dirty
            for step in lane_steps
        )
        dirty_evictions = sum(
            step.evidence.evicted_way is not None and step.evidence.victim_dirty
            for step in lane_steps
        )
        snapshot = (
            lane_steps[-1].after_cache_snapshot
            if lane_steps
            else self.get_cache_snapshot(lane.lane_id)
        )
        final_dirty_lines = sum(line.valid and line.dirty for line in snapshot)
        final_dirty_bytes = final_dirty_lines * self.config.block_size_bytes
        memory_write_bytes = sum(delta.memory_write_bytes for delta in traffic)
        total_bytes = sum(delta.total_lower_memory_bytes for delta in traffic)
        return WritePolicyLaneStatistics(
            lane=lane,
            accesses=accesses,
            reads=reads,
            writes=writes,
            hits=hits,
            misses=accesses - hits,
            read_hits=read_hits,
            read_misses=read_misses,
            write_hits=write_hits,
            write_misses=write_misses,
            write_miss_allocations=write_allocations,
            write_miss_bypasses=write_bypasses,
            block_fills=sum(delta.block_fills for delta in traffic),
            clean_evictions=clean_evictions,
            dirty_evictions=dirty_evictions,
            immediate_store_writes=sum(delta.immediate_store_writes for delta in traffic),
            bypass_writes=sum(delta.bypass_writes for delta in traffic),
            dirty_writebacks=sum(delta.dirty_writebacks for delta in traffic),
            memory_read_transactions=sum(delta.memory_read_transactions for delta in traffic),
            memory_read_bytes=sum(delta.memory_read_bytes for delta in traffic),
            memory_write_transactions=sum(delta.memory_write_transactions for delta in traffic),
            memory_write_bytes=memory_write_bytes,
            total_lower_memory_transactions=sum(delta.total_lower_memory_transactions for delta in traffic),
            total_lower_memory_bytes=total_bytes,
            final_dirty_lines=final_dirty_lines,
            final_dirty_bytes=final_dirty_bytes,
            memory_write_bytes_with_final_drain=memory_write_bytes + final_dirty_bytes,
            total_lower_memory_bytes_with_final_drain=total_bytes + final_dirty_bytes,
        )


def _divergences(lane_steps):
    evidences = tuple(step.evidence for step in lane_steps)
    outcome = len({evidence.cache_hit for evidence in evidences}) > 1
    allocation = len({evidence.allocated for evidence in evidences}) > 1
    bypass = len({evidence.bypassed for evidence in evidences}) > 1
    writeback = len({evidence.traffic_delta.dirty_writebacks for evidence in evidences}) > 1
    traffic = len({evidence.traffic_delta.total_lower_memory_bytes for evidence in evidences}) > 1
    dirty_signatures = {
        tuple(line.valid and line.dirty for line in step.after_cache_snapshot)
        for step in lane_steps
    }
    cache_signatures = {step.after_cache_snapshot for step in lane_steps}
    return (
        outcome,
        allocation,
        bypass,
        writeback,
        traffic,
        len(dirty_signatures) > 1,
        len(cache_signatures) > 1,
    )


__all__ = ["WritePolicyComparisonSession"]
