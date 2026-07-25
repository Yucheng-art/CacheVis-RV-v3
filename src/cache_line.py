"""Cache line model used by the simulator."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CacheLine:
    """Represents one way inside one cache set."""

    valid: bool = False
    tag: Optional[int] = None
    dirty: bool = False
    last_used: int = 0
    insert_time: int = 0
