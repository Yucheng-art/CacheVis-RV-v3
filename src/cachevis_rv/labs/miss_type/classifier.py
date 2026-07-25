"""Pure classifier implementing the strict foundational 3C miss rules."""

from .model import MissType, MissTypeEvidence


class MissTypeClassifier:
    """Classify actual misses using a fully-associative LRU reference result."""

    def __init__(self) -> None:
        self._seen_blocks: set[int] = set()

    @property
    def seen_blocks(self) -> frozenset[int]:
        """Return an immutable snapshot of memory blocks seen in this trace."""
        return frozenset(self._seen_blocks)

    def reset(self) -> None:
        """Forget all blocks from the current trace."""
        self._seen_blocks.clear()

    def classify(
        self,
        block_address: int,
        *,
        actual_hit: bool,
        reference_hit: bool,
    ) -> tuple[MissType | None, MissTypeEvidence]:
        """Return the 3C miss type and evidence for one synchronized access."""
        self._validate_input(block_address, actual_hit, reference_hit)
        seen_before = block_address in self._seen_blocks

        if not seen_before and actual_hit:
            raise ValueError("first access to a memory block cannot be an actual hit")
        if not seen_before and reference_hit:
            raise ValueError("first access to a memory block cannot be a reference hit")

        if actual_hit:
            miss_type = None
            reason = "Actual cache hit; hit accesses do not have a miss type."
        elif not seen_before:
            miss_type = MissType.COMPULSORY
            reason = "First access to this memory block; classify as compulsory."
        elif reference_hit:
            miss_type = MissType.CONFLICT
            reason = (
                "Block was seen before and the fully-associative LRU reference hit; "
                "the actual miss is caused by set placement."
            )
        else:
            miss_type = MissType.CAPACITY
            reason = (
                "Block was seen before and the same-capacity fully-associative LRU "
                "reference also missed; classify as capacity."
            )

        evidence = MissTypeEvidence(
            seen_before=seen_before,
            actual_hit=actual_hit,
            reference_hit=reference_hit,
            actual_miss=not actual_hit,
            reference_miss=not reference_hit,
            classification_reason=reason,
        )
        self._seen_blocks.add(block_address)
        return miss_type, evidence

    @staticmethod
    def _validate_input(
        block_address: int,
        actual_hit: bool,
        reference_hit: bool,
    ) -> None:
        if isinstance(block_address, bool) or not isinstance(block_address, int):
            raise TypeError("block_address must be an integer")
        if block_address < 0:
            raise ValueError("block_address must be non-negative")
        if not isinstance(actual_hit, bool):
            raise TypeError("actual_hit must be a bool")
        if not isinstance(reference_hit, bool):
            raise TypeError("reference_hit must be a bool")


__all__ = ["MissTypeClassifier"]
