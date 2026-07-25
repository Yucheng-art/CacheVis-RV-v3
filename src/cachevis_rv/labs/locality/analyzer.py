"""Stateful pure-Python primary locality evidence analyzer."""

from .model import LocalityEvidence, LocalityKind


class LocalityAnalyzer:
    """Classify trace accesses without consulting cache hit/miss results."""

    def __init__(self) -> None:
        self.reset()

    @property
    def seen_addresses(self) -> frozenset[int]:
        """Return all concrete addresses observed so far."""
        return frozenset(self._seen_addresses)

    @property
    def seen_blocks(self) -> frozenset[int]:
        """Return all memory blocks observed so far."""
        return frozenset(self._seen_blocks)

    def reset(self) -> None:
        """Clear all history, last-use indexes, offsets, and recency state."""
        self._seen_addresses: set[int] = set()
        self._seen_blocks: set[int] = set()
        self._seen_offsets_by_block: dict[int, set[int]] = {}
        self._last_address_step: dict[int, int] = {}
        self._last_block_step: dict[int, int] = {}
        self._block_recency: list[int] = []
        self._previous_address: int | None = None
        self._previous_block: int | None = None
        self._last_step_index: int | None = None

    def analyze(
        self,
        address: int,
        block_size_bytes: int,
        step_index: int,
    ) -> tuple[LocalityKind, LocalityEvidence]:
        """Classify one address, publish pre-access evidence, and update history."""
        self._require_non_negative_int("address", address)
        self._require_positive_int("block_size_bytes", block_size_bytes)
        self._require_non_negative_int("step_index", step_index)
        if self._last_step_index is not None and step_index <= self._last_step_index:
            raise ValueError("step_index must increase for each analyzed access")

        block_address = address // block_size_bytes
        offset = address % block_size_bytes
        address_seen = address in self._seen_addresses
        block_seen = block_address in self._seen_blocks
        offset_seen = offset in self._seen_offsets_by_block.get(block_address, set())
        previous_address_step = self._last_address_step.get(address)
        previous_block_step = self._last_block_step.get(block_address)
        address_reuse_gap = (
            step_index - previous_address_step
            if previous_address_step is not None
            else None
        )
        block_reuse_gap = (
            step_index - previous_block_step
            if previous_block_step is not None
            else None
        )
        block_reuse_distance = (
            self._block_recency.index(block_address) if block_seen else None
        )
        same_block_as_previous = (
            self._previous_block is not None
            and block_address == self._previous_block
        )
        address_delta = (
            address - self._previous_address
            if self._previous_address is not None
            else None
        )

        if address_seen:
            kind = LocalityKind.TEMPORAL
            reason = (
                "This exact address was accessed before, so the primary "
                "evidence is temporal reuse."
            )
        elif block_seen:
            kind = LocalityKind.SPATIAL
            reason = (
                "This address is new, but its memory block was accessed before, "
                "so the primary evidence is spatial locality."
            )
        else:
            kind = LocalityKind.FIRST_TOUCH
            reason = (
                "This memory block has not been accessed before; this is a first "
                "touch, not a positive locality event."
            )

        evidence = LocalityEvidence(
            address_seen_before=address_seen,
            block_seen_before=block_seen,
            offset_seen_before=offset_seen,
            previous_address_step=previous_address_step,
            previous_block_step=previous_block_step,
            address_reuse_gap=address_reuse_gap,
            block_reuse_gap=block_reuse_gap,
            block_reuse_distance=block_reuse_distance,
            same_block_as_previous=same_block_as_previous,
            address_delta=address_delta,
            classification_reason=reason,
        )
        self._update_history(address, block_address, offset, step_index)
        return kind, evidence

    def _update_history(
        self,
        address: int,
        block_address: int,
        offset: int,
        step_index: int,
    ) -> None:
        self._seen_addresses.add(address)
        self._seen_blocks.add(block_address)
        self._seen_offsets_by_block.setdefault(block_address, set()).add(offset)
        self._last_address_step[address] = step_index
        self._last_block_step[block_address] = step_index
        if block_address in self._block_recency:
            self._block_recency.remove(block_address)
        self._block_recency.insert(0, block_address)
        self._previous_address = address
        self._previous_block = block_address
        self._last_step_index = step_index

    @staticmethod
    def _require_non_negative_int(name: str, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    @staticmethod
    def _require_positive_int(name: str, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")


__all__ = ["LocalityAnalyzer"]
