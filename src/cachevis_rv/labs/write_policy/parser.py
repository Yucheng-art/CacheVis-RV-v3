"""Strict parser for read/write byte-address traces."""

import re

from .model import MemoryAccess, MemoryAccessKind


_ITEM_PATTERN = re.compile(r"^\s*([A-Za-z]+)\s*(?::|\s)\s*(\S+)\s*$")


def parse_memory_access_trace(text: str) -> tuple[MemoryAccess, ...]:
    if not isinstance(text, str):
        raise ValueError("trace must be text")
    if not text.strip():
        return ()

    comma_parts = text.split(",")
    if any(not part.strip() for part in comma_parts):
        raise ValueError("trace contains an empty item")

    items: list[str] = []
    for part in comma_parts:
        items.extend(line.strip() for line in part.splitlines() if line.strip())

    accesses: list[MemoryAccess] = []
    for item in items:
        match = _ITEM_PATTERN.fullmatch(item)
        if match is None:
            operation = item.split(maxsplit=1)[0] if item.split() else ""
            if operation.upper() in {"R", "W"}:
                raise ValueError(f"invalid or missing address in trace item: {item!r}")
            raise ValueError(f"unknown operation or extra fields in trace item: {item!r}")
        operation, address_token = match.groups()
        operation = operation.upper()
        if operation not in {"R", "W"}:
            raise ValueError(f"unknown operation: {operation!r}")
        try:
            address = int(address_token, 0)
        except ValueError as exc:
            raise ValueError(f"invalid address token: {address_token!r}") from exc
        if address < 0:
            raise ValueError("address must be non-negative")
        kind = MemoryAccessKind.READ if operation == "R" else MemoryAccessKind.WRITE
        accesses.append(MemoryAccess(kind, address))
    return tuple(accesses)


__all__ = ["parse_memory_access_trace"]
