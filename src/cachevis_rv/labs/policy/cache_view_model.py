"""Pure presentation models for the three policy cache lanes."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .model import PolicyComparisonStep, PolicyDecisionKind, PolicyLineSnapshot
from .session import PolicyComparisonSession


@dataclass(frozen=True)
class PolicyCacheLineViewModel:
    policy: str
    set_index: int
    way: int
    valid: bool
    tag: int | None
    dirty: bool
    last_used: int
    insert_time: int
    is_current_set: bool
    is_hit_way: bool
    is_fill_way: bool
    is_victim_way: bool
    is_valid_candidate: bool
    is_eligible_victim: bool
    is_changed_by_current_access: bool


@dataclass(frozen=True)
class PolicyLaneCacheViewModel:
    policy: str
    config: CacheConfig
    cache_lines: tuple[PolicyCacheLineViewModel, ...]
    current_cache_hit: bool | None
    current_decision_kind: PolicyDecisionKind | None
    current_set_index: int | None
    current_hit_way: int | None
    current_fill_way: int | None
    current_victim_way: int | None
    current_victim_tag: int | None


def build_lane_cache_view_models(
    session: PolicyComparisonSession,
    current_step: PolicyComparisonStep | None,
) -> tuple[PolicyLaneCacheViewModel, ...]:
    """Build LRU/FIFO/Random cache lanes from the latest session snapshots."""
    lanes = []
    for policy in session.policies:
        snapshot = session.get_cache_snapshot(policy)
        lane_step = _lane_for(current_step, policy)
        evidence = lane_step.decision if lane_step is not None else None
        before_by_way = (
            {line.way: line for line in lane_step.before_set_lines}
            if lane_step is not None
            else {}
        )
        after_by_way = (
            {line.way: line for line in lane_step.after_set_lines}
            if lane_step is not None
            else {}
        )
        lines = tuple(
            _build_line(
                policy,
                line,
                evidence,
                before_by_way,
                after_by_way,
            )
            for cache_set in snapshot
            for line in sorted(cache_set, key=lambda item: item.way)
        )
        lanes.append(
            PolicyLaneCacheViewModel(
                policy=policy,
                config=session.policy_config(policy),
                cache_lines=lines,
                current_cache_hit=(
                    lane_step.cache_hit if lane_step is not None else None
                ),
                current_decision_kind=(
                    evidence.decision_kind if evidence is not None else None
                ),
                current_set_index=(
                    evidence.set_index if evidence is not None else None
                ),
                current_hit_way=evidence.hit_way if evidence is not None else None,
                current_fill_way=(
                    evidence.fill_way if evidence is not None else None
                ),
                current_victim_way=(
                    evidence.victim_way if evidence is not None else None
                ),
                current_victim_tag=(
                    evidence.victim_tag if evidence is not None else None
                ),
            )
        )
    return tuple(lanes)


def _build_line(
    policy: str,
    line: PolicyLineSnapshot,
    evidence,
    before_by_way: dict[int, PolicyLineSnapshot],
    after_by_way: dict[int, PolicyLineSnapshot],
) -> PolicyCacheLineViewModel:
    in_current_set = evidence is not None and line.set_index == evidence.set_index
    changed = (
        in_current_set
        and line.way in before_by_way
        and line.way in after_by_way
        and before_by_way[line.way] != after_by_way[line.way]
    )
    return PolicyCacheLineViewModel(
        policy=policy,
        set_index=line.set_index,
        way=line.way,
        valid=line.valid,
        tag=line.tag,
        dirty=line.dirty,
        last_used=line.last_used,
        insert_time=line.insert_time,
        is_current_set=in_current_set,
        is_hit_way=in_current_set and line.way == evidence.hit_way,
        is_fill_way=in_current_set and line.way == evidence.fill_way,
        is_victim_way=in_current_set and line.way == evidence.victim_way,
        is_valid_candidate=(
            in_current_set
            and evidence.decision_kind is PolicyDecisionKind.EVICTION
            and line.way in evidence.valid_ways_before
        ),
        is_eligible_victim=(
            in_current_set and line.way in evidence.eligible_victim_ways
        ),
        is_changed_by_current_access=changed,
    )


def _lane_for(step: PolicyComparisonStep | None, policy: str):
    if step is None:
        return None
    return next(lane for lane in step.lane_steps if lane.policy == policy)


__all__ = [
    "PolicyCacheLineViewModel",
    "PolicyLaneCacheViewModel",
    "build_lane_cache_view_models",
]
