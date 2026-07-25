"""Compatibility facade for Address Explorer bit segments."""

from cachevis_rv.labs.address_explorer.address_bits import (
    AddressBitSegment,
    split_address_bit_segments,
)

__all__ = ["AddressBitSegment", "split_address_bit_segments"]
