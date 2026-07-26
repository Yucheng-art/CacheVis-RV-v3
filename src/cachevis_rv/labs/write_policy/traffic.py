"""Lower-memory traffic formulas for one explained cache access."""

from .model import WriteTrafficDelta


def build_traffic_delta(
    *,
    block_size_bytes: int,
    store_size_bytes: int,
    block_fills: int = 0,
    immediate_store_writes: int = 0,
    bypass_writes: int = 0,
    dirty_writebacks: int = 0,
) -> WriteTrafficDelta:
    counts = (
        block_fills,
        immediate_store_writes,
        bypass_writes,
        dirty_writebacks,
    )
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts):
        raise ValueError("traffic counts must be non-negative integers")
    if isinstance(block_size_bytes, bool) or not isinstance(block_size_bytes, int) or block_size_bytes <= 0:
        raise ValueError("block_size_bytes must be a positive integer")
    if isinstance(store_size_bytes, bool) or not isinstance(store_size_bytes, int) or store_size_bytes <= 0:
        raise ValueError("store_size_bytes must be a positive integer")

    block_fill_bytes = block_fills * block_size_bytes
    immediate_store_bytes = immediate_store_writes * store_size_bytes
    bypass_write_bytes = bypass_writes * store_size_bytes
    dirty_writeback_bytes = dirty_writebacks * block_size_bytes
    memory_write_transactions = (
        immediate_store_writes + bypass_writes + dirty_writebacks
    )
    memory_write_bytes = (
        immediate_store_bytes + bypass_write_bytes + dirty_writeback_bytes
    )
    return WriteTrafficDelta(
        block_fills=block_fills,
        block_fill_bytes=block_fill_bytes,
        immediate_store_writes=immediate_store_writes,
        immediate_store_bytes=immediate_store_bytes,
        bypass_writes=bypass_writes,
        bypass_write_bytes=bypass_write_bytes,
        dirty_writebacks=dirty_writebacks,
        dirty_writeback_bytes=dirty_writeback_bytes,
        memory_read_transactions=block_fills,
        memory_read_bytes=block_fill_bytes,
        memory_write_transactions=memory_write_transactions,
        memory_write_bytes=memory_write_bytes,
        total_lower_memory_transactions=block_fills + memory_write_transactions,
        total_lower_memory_bytes=block_fill_bytes + memory_write_bytes,
    )


__all__ = ["build_traffic_delta"]
