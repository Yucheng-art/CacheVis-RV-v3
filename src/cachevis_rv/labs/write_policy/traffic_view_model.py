"""Presentation-neutral views of one access's lower-memory traffic."""

from dataclasses import dataclass

from .model import WriteTrafficDelta


@dataclass(frozen=True)
class WritePolicyTrafficViewModel:
    block_fills: int
    block_fill_bytes: int
    immediate_store_writes: int
    immediate_store_bytes: int
    bypass_writes: int
    bypass_write_bytes: int
    dirty_writebacks: int
    dirty_writeback_bytes: int
    memory_read_transactions: int
    memory_read_bytes: int
    memory_write_transactions: int
    memory_write_bytes: int
    total_lower_memory_transactions: int
    total_lower_memory_bytes: int
    transaction_decomposition_ok: bool
    byte_decomposition_ok: bool


def build_traffic_view_model(delta: WriteTrafficDelta) -> WritePolicyTrafficViewModel:
    """Copy formal traffic values and verify their published decompositions."""
    if not isinstance(delta, WriteTrafficDelta):
        raise ValueError("delta must be a WriteTrafficDelta")
    write_transactions = (
        delta.immediate_store_writes + delta.bypass_writes + delta.dirty_writebacks
    )
    write_bytes = (
        delta.immediate_store_bytes
        + delta.bypass_write_bytes
        + delta.dirty_writeback_bytes
    )
    return WritePolicyTrafficViewModel(
        **{name: getattr(delta, name) for name in delta.__dataclass_fields__},
        transaction_decomposition_ok=(
            delta.memory_read_transactions == delta.block_fills
            and delta.memory_write_transactions == write_transactions
            and delta.total_lower_memory_transactions
            == delta.memory_read_transactions + delta.memory_write_transactions
        ),
        byte_decomposition_ok=(
            delta.memory_read_bytes == delta.block_fill_bytes
            and delta.memory_write_bytes == write_bytes
            and delta.total_lower_memory_bytes
            == delta.memory_read_bytes + delta.memory_write_bytes
        ),
    )


__all__ = ["WritePolicyTrafficViewModel", "build_traffic_view_model"]
