"""Pure helpers for Tag / Index / Offset bit segment display."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AddressBitSegment:
    """One labeled segment in a binary address bar."""

    name: str
    bits: str
    bit_count: int
    value: int
    high_bit: Optional[int]
    low_bit: Optional[int]
    range_label: str


def split_address_bit_segments(
    address_binary: str,
    tag_bits: int,
    index_bits: int,
    offset_bits: int,
    tag: int,
    index: int,
    offset: int,
) -> list[AddressBitSegment]:
    """Split a binary address string into Tag, Index, and Offset segments."""
    _validate_binary(address_binary)
    _validate_bit_count("tag_bits", tag_bits)
    _validate_bit_count("index_bits", index_bits)
    _validate_bit_count("offset_bits", offset_bits)

    address_bits = len(address_binary)
    if tag_bits + index_bits + offset_bits != address_bits:
        raise ValueError("tag_bits + index_bits + offset_bits must equal address length")

    tag_end = tag_bits
    index_end = tag_end + index_bits
    return [
        _make_segment(
            "Tag",
            address_binary[:tag_end],
            tag_bits,
            tag,
            high_bit=address_bits - 1,
            low_bit=index_bits + offset_bits,
        ),
        _make_segment(
            "Index",
            address_binary[tag_end:index_end],
            index_bits,
            index,
            high_bit=offset_bits + index_bits - 1,
            low_bit=offset_bits,
        ),
        _make_segment(
            "Offset",
            address_binary[index_end:],
            offset_bits,
            offset,
            high_bit=offset_bits - 1,
            low_bit=0,
        ),
    ]


def _make_segment(
    name: str,
    bits: str,
    bit_count: int,
    value: int,
    *,
    high_bit: int,
    low_bit: int,
) -> AddressBitSegment:
    if bit_count == 0:
        return AddressBitSegment(
            name=name,
            bits="",
            bit_count=0,
            value=value,
            high_bit=None,
            low_bit=None,
            range_label=f"{name}: none (0 bits)",
        )
    return AddressBitSegment(
        name=name,
        bits=bits,
        bit_count=bit_count,
        value=value,
        high_bit=high_bit,
        low_bit=low_bit,
        range_label=f"{name}: bits [{high_bit}:{low_bit}]",
    )


def _validate_binary(address_binary: str) -> None:
    if not address_binary:
        raise ValueError("address_binary must not be empty")
    if any(bit not in {"0", "1"} for bit in address_binary):
        raise ValueError("address_binary must contain only 0 and 1")


def _validate_bit_count(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
