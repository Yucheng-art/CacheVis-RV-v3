"""Explain formal core results without simulating or selecting victims."""

from cachevis_rv.core import CacheConfig

from .model import (
    CacheSnapshot,
    MemoryAccess,
    MemoryAccessKind,
    WriteDecisionKind,
    WritePolicyDecisionEvidence,
    WritePolicyLaneSpec,
    WritePolicyLineSnapshot,
    WriteTrafficAssumptions,
)
from .traffic import build_traffic_delta


def snapshot_cache(raw_snapshot: list[list[dict[str, object]]]) -> CacheSnapshot:
    lines = tuple(
        WritePolicyLineSnapshot(
            set_index=int(line["set_index"]),
            way=int(line["way"]),
            valid=bool(line["valid"]),
            tag=None if line["tag"] is None else int(line["tag"]),
            dirty=bool(line["dirty"]),
            last_used=int(line["last_used"]),
            insert_time=int(line["insert_time"]),
        )
        for cache_set in raw_snapshot
        for line in cache_set
    )
    return tuple(sorted(lines, key=lambda line: (line.set_index, line.way)))


def _line_at(
    snapshot: CacheSnapshot, set_index: int, way: int | None
) -> WritePolicyLineSnapshot | None:
    if way is None:
        return None
    matches = tuple(
        line for line in snapshot if line.set_index == set_index and line.way == way
    )
    if len(matches) != 1:
        raise ValueError(
            f"snapshot does not uniquely identify set {set_index}, way {way}"
        )
    return matches[0]


class WritePolicyExplainer:
    @staticmethod
    def explain(
        lane: WritePolicyLaneSpec,
        access: MemoryAccess,
        assumptions: WriteTrafficAssumptions,
        config: CacheConfig,
        before_cache_snapshot: CacheSnapshot,
        access_result: dict[str, object],
        after_cache_snapshot: CacheSnapshot,
    ) -> WritePolicyDecisionEvidence:
        operation = access.kind.value
        hit = bool(access_result["hit"])
        allocated = bool(access_result["allocated"])
        bypassed = bool(access_result["bypassed"])
        hit_way = _optional_int(access_result["hit_way"])
        fill_way = _optional_int(access_result["fill_way"])
        evicted_way = _optional_int(access_result["evicted_way"])
        victim_tag = _optional_int(access_result["victim_tag"])
        victim_dirty = bool(access_result["victim_dirty"])
        line_dirty_before = _optional_bool(access_result["line_dirty_before"])
        line_dirty_after = _optional_bool(access_result["line_dirty_after"])
        set_index = int(access_result["index"])
        tag = int(access_result["tag"])

        decision_kind = _decision_kind(lane, access, hit, allocated, bypassed)
        block_fills = int(not hit and allocated)
        immediate_stores = int(
            access.kind is MemoryAccessKind.WRITE
            and lane.write_policy == "write-through"
            and (hit or allocated)
        )
        bypass_writes = int(
            access.kind is MemoryAccessKind.WRITE and bypassed
        )
        dirty_writebacks = int(evicted_way is not None and victim_dirty)
        traffic = build_traffic_delta(
            block_size_bytes=config.block_size_bytes,
            store_size_bytes=assumptions.store_size_bytes,
            block_fills=block_fills,
            immediate_store_writes=immediate_stores,
            bypass_writes=bypass_writes,
            dirty_writebacks=dirty_writebacks,
        )

        before_set = tuple(
            line for line in before_cache_snapshot if line.set_index == set_index
        )
        after_set = tuple(
            line for line in after_cache_snapshot if line.set_index == set_index
        )
        before_evicted = _line_at(before_cache_snapshot, set_index, evicted_way)
        before_fill = _line_at(before_cache_snapshot, set_index, fill_way)
        before_target = _line_at(
            before_cache_snapshot, set_index, hit_way if hit else fill_way
        )
        after_target = _line_at(
            after_cache_snapshot, set_index, hit_way if hit else fill_way
        )

        checks = [
            access_result["operation"] == operation,
            not (allocated and bypassed),
            lane.write_policy == config.write_policy,
            lane.write_allocate == config.write_allocate,
            int(access_result["address"]) == access.address,
        ]
        if hit:
            checks.extend(
                (not allocated, not bypassed, hit_way is not None, fill_way is None,
                 evicted_way is None)
            )
        elif bypassed:
            checks.extend(
                (
                    not allocated,
                    hit_way is None,
                    fill_way is None,
                    evicted_way is None,
                    victim_tag is None,
                    not victim_dirty,
                    before_cache_snapshot == after_cache_snapshot,
                    line_dirty_before is None,
                    line_dirty_after is None,
                )
            )
        else:
            checks.extend((allocated, fill_way is not None, hit_way is None))
            if evicted_way is None:
                checks.extend(
                    (
                        before_fill is not None and not before_fill.valid,
                        victim_tag is None,
                        not victim_dirty,
                    )
                )
            else:
                checks.extend(
                    (
                        before_evicted is not None and before_evicted.valid,
                        before_evicted is not None
                        and before_evicted.tag == victim_tag,
                        before_evicted is not None
                        and before_evicted.dirty == victim_dirty,
                        fill_way == evicted_way,
                    )
                )

        if after_target is not None:
            checks.extend(
                (
                    after_target.tag == tag,
                    after_target.dirty == line_dirty_after,
                    before_target is not None
                    and before_target.dirty == line_dirty_before,
                )
            )
        if access.kind is MemoryAccessKind.READ and hit:
            checks.append(line_dirty_before == line_dirty_after)
        if access.kind is MemoryAccessKind.READ and not hit:
            checks.append(line_dirty_after is False)
        if access.kind is MemoryAccessKind.WRITE and (hit or allocated):
            expected_dirty = lane.write_policy == "write-back"
            checks.extend(
                (
                    line_dirty_after is expected_dirty,
                    after_target is not None and after_target.dirty is expected_dirty,
                )
            )
        if evicted_way is None:
            checks.append(traffic.dirty_writebacks == 0)
        else:
            checks.append(traffic.dirty_writebacks == int(victim_dirty))

        reason, rule_path = _description(decision_kind, victim_dirty)
        return WritePolicyDecisionEvidence(
            lane=lane,
            access=access,
            decision_kind=decision_kind,
            block_address=access.address // config.block_size_bytes,
            set_index=set_index,
            tag=tag,
            cache_hit=hit,
            allocated=allocated,
            bypassed=bypassed,
            hit_way=hit_way,
            fill_way=fill_way,
            evicted_way=evicted_way,
            victim_tag=victim_tag,
            victim_dirty=victim_dirty,
            line_dirty_before=line_dirty_before,
            line_dirty_after=line_dirty_after,
            before_set_lines=before_set,
            after_set_lines=after_set,
            traffic_delta=traffic,
            classification_reason=reason,
            rule_path=rule_path,
            metadata_consistent=all(checks),
        )


def _decision_kind(lane, access, hit, allocated, bypassed):
    if access.kind is MemoryAccessKind.READ:
        if bypassed or (not hit and not allocated):
            raise ValueError("a read miss must allocate and may not bypass")
        return WriteDecisionKind.READ_HIT if hit else WriteDecisionKind.READ_MISS_FILL
    if hit:
        return (
            WriteDecisionKind.WRITE_HIT_THROUGH
            if lane.write_policy == "write-through"
            else WriteDecisionKind.WRITE_HIT_BACK
        )
    if bypassed:
        return WriteDecisionKind.WRITE_MISS_BYPASS
    if not allocated:
        raise ValueError("a write miss must allocate or bypass")
    return (
        WriteDecisionKind.WRITE_MISS_ALLOCATE_THROUGH
        if lane.write_policy == "write-through"
        else WriteDecisionKind.WRITE_MISS_ALLOCATE_BACK
    )


def _description(kind, victim_dirty):
    paths = {
        WriteDecisionKind.READ_HIT: ("Read hit; no lower-memory transfer.", ("read", "hit")),
        WriteDecisionKind.READ_MISS_FILL: ("Read miss fills one cache block.", ("read", "miss", "allocate", "fill")),
        WriteDecisionKind.WRITE_HIT_THROUGH: ("Write hit updates the clean line and writes the store through.", ("write", "hit", "write-through")),
        WriteDecisionKind.WRITE_HIT_BACK: ("Write hit marks the resident line dirty.", ("write", "hit", "write-back", "mark-dirty")),
        WriteDecisionKind.WRITE_MISS_ALLOCATE_THROUGH: ("Write miss fills a block and writes the store through.", ("write", "miss", "allocate", "fill", "write-through")),
        WriteDecisionKind.WRITE_MISS_ALLOCATE_BACK: ("Write miss fills a block and marks it dirty.", ("write", "miss", "allocate", "fill", "write-back")),
        WriteDecisionKind.WRITE_MISS_BYPASS: ("Write miss bypasses the cache and writes the store to lower memory.", ("write", "miss", "no-write-allocate", "bypass")),
    }
    reason, path = paths[kind]
    if victim_dirty:
        return reason + " The dirty victim is written back first.", path + ("dirty-writeback",)
    return reason, path


def _optional_int(value):
    return None if value is None else int(value)


def _optional_bool(value):
    return None if value is None else bool(value)


__all__ = ["WritePolicyExplainer", "snapshot_cache"]
