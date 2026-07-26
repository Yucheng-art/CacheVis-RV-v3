"""Explain and validate decisions already made by CacheSimulator."""

from collections.abc import Mapping

from .model import (
    PolicyDecisionEvidence,
    PolicyDecisionKind,
    PolicyLineSnapshot,
)


POLICIES = ("LRU", "FIFO", "Random")


class PolicyDecisionExplainer:
    """Observe before/result/after data without choosing a victim."""

    @classmethod
    def explain(
        cls,
        policy: str,
        before_set_lines: tuple[PolicyLineSnapshot, ...],
        access_result: Mapping[str, object],
        after_set_lines: tuple[PolicyLineSnapshot, ...],
        *,
        random_seed: int | None = None,
        random_draw_index: int | None = None,
    ) -> PolicyDecisionEvidence:
        if policy not in POLICIES:
            raise ValueError(f"unsupported replacement policy: {policy}")
        if not before_set_lines or len(before_set_lines) != len(after_set_lines):
            raise ValueError("before and after target-set snapshots must match")

        set_index = int(access_result["index"])
        tag = int(access_result["tag"])
        actual_way = int(access_result["victim_way"])
        hit = bool(access_result["hit"])
        replaced_valid = bool(access_result["replaced_valid"])
        valid = tuple(line.way for line in before_set_lines if line.valid)
        invalid = tuple(line.way for line in before_set_lines if not line.valid)
        lru_order = tuple(
            line.way for line in sorted(
                (line for line in before_set_lines if line.valid),
                key=lambda line: (line.last_used, line.way),
            )
        )
        fifo_order = tuple(
            line.way for line in sorted(
                (line for line in before_set_lines if line.valid),
                key=lambda line: (line.insert_time, line.way),
            )
        )

        if hit:
            kind = PolicyDecisionKind.HIT
            hit_way, fill_way, victim_way, victim_tag = actual_way, None, None, None
            eligible = ()
            random_candidates = ()
            selected_metric = None
            consistent = (
                not replaced_valid
                and access_result["replaced_tag"] is None
                and cls._hit_consistent(
                    before_set_lines, after_set_lines, actual_way, tag
                )
            )
            reason = (
                "The target tag was already valid in this set; no fill or "
                "replacement occurred."
            )
        elif not replaced_valid:
            kind = PolicyDecisionKind.INVALID_FILL
            hit_way, fill_way, victim_way, victim_tag = None, actual_way, None, None
            eligible = ()
            random_candidates = ()
            selected_metric = None
            consistent = (
                access_result["replaced_tag"] is None
                and cls._invalid_fill_consistent(
                    before_set_lines, after_set_lines, actual_way, tag
                )
            )
            reason = (
                f"Way {actual_way} was invalid before the miss, so it was filled; "
                "no valid line was evicted."
            )
        else:
            kind = PolicyDecisionKind.EVICTION
            hit_way, fill_way, victim_way = None, None, actual_way
            before_victim = cls._line_by_way(before_set_lines, actual_way)
            victim_tag = before_victim.tag
            random_candidates = valid if policy == "Random" else ()
            valid_lines = tuple(line for line in before_set_lines if line.valid)
            if policy == "LRU":
                minimum = min(line.last_used for line in valid_lines)
                eligible = tuple(
                    line.way for line in valid_lines
                    if line.last_used == minimum
                )
                selected_metric = before_victim.last_used
                reason = (
                    f"Full-set miss: way {actual_way} was selected from the "
                    f"least-recently-used candidate(s) {eligible}."
                )
            elif policy == "FIFO":
                minimum = min(line.insert_time for line in valid_lines)
                eligible = tuple(
                    line.way for line in valid_lines
                    if line.insert_time == minimum
                )
                selected_metric = before_victim.insert_time
                reason = (
                    f"Full-set miss: way {actual_way} was selected from the "
                    f"oldest-inserted candidate(s) {eligible}."
                )
            else:
                eligible = valid
                selected_metric = None
                reason = (
                    f"Full-set miss: seeded random replay selected way {actual_way} "
                    f"from all valid candidates {eligible}."
                )
            consistent = (
                not invalid
                and actual_way in eligible
                and victim_tag == access_result["replaced_tag"]
                and cls._eviction_consistent(
                    before_set_lines, after_set_lines, actual_way, tag
                )
            )

        return PolicyDecisionEvidence(
            policy=policy,
            decision_kind=kind,
            set_index=set_index,
            tag=tag,
            hit_way=hit_way,
            fill_way=fill_way,
            victim_way=victim_way,
            victim_tag=victim_tag,
            valid_ways_before=valid,
            invalid_ways_before=invalid,
            eligible_victim_ways=eligible,
            lru_order_before=lru_order,
            fifo_order_before=fifo_order,
            random_candidate_ways=random_candidates,
            selected_metric=selected_metric,
            classification_reason=reason,
            metadata_consistent=consistent,
            random_seed=random_seed if policy == "Random" else None,
            random_draw_index=(
                random_draw_index
                if policy == "Random"
                and kind is PolicyDecisionKind.EVICTION
                else None
            ),
        )

    @staticmethod
    def _line_by_way(
        lines: tuple[PolicyLineSnapshot, ...], way: int
    ) -> PolicyLineSnapshot:
        try:
            return next(line for line in lines if line.way == way)
        except StopIteration as exc:
            raise ValueError(f"way {way} is absent from target-set snapshot") from exc

    @classmethod
    def _hit_consistent(cls, before, after, way, tag) -> bool:
        before_line = cls._line_by_way(before, way)
        after_line = cls._line_by_way(after, way)
        return (
            before_line.valid and before_line.tag == tag
            and after_line.valid and after_line.tag == tag
            and all(
                cls._same_line_content(old, cls._line_by_way(after, old.way))
                for old in before if old.way != way
            )
        )

    @classmethod
    def _invalid_fill_consistent(cls, before, after, way, tag) -> bool:
        old = cls._line_by_way(before, way)
        new = cls._line_by_way(after, way)
        changed = [
            line.way for line in before
            if line != cls._line_by_way(after, line.way)
        ]
        return (
            not old.valid and new.valid and new.tag == tag
            and changed == [way]
        )

    @classmethod
    def _eviction_consistent(cls, before, after, way, tag) -> bool:
        old = cls._line_by_way(before, way)
        new = cls._line_by_way(after, way)
        changed = [
            line.way for line in before
            if line != cls._line_by_way(after, line.way)
        ]
        return old.valid and new.valid and new.tag == tag and changed == [way]

    @staticmethod
    def _same_line_content(
        left: PolicyLineSnapshot, right: PolicyLineSnapshot
    ) -> bool:
        return left == right


__all__ = ["POLICIES", "PolicyDecisionExplainer"]
