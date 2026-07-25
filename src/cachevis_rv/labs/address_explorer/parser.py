"""Parse user-entered address traces for visual cache stepping."""

import re


_SEPARATOR_RE = re.compile(r"[\s,]+")


def parse_address_trace(text: str) -> list[int]:
    """Parse decimal and hex addresses separated by whitespace or commas."""
    if text is None or not text.strip():
        raise ValueError("address trace must not be empty")

    addresses: list[int] = []
    for token in _SEPARATOR_RE.split(text.strip()):
        if not token:
            continue
        addresses.append(_parse_address_token(token))

    if not addresses:
        raise ValueError("address trace must contain at least one address")
    return addresses


def _parse_address_token(token: str) -> int:
    try:
        address = int(token, 0)
    except ValueError as exc:
        raise ValueError(f"invalid address token: {token!r}") from exc

    if address < 0:
        raise ValueError(f"address must be non-negative: {token!r}")
    return address
