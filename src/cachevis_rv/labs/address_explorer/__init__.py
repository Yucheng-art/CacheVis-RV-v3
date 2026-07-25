"""Pure logic API for the Address Explorer lab.

GUI widgets are intentionally not imported here so importing this package has
no PySide6 side effects.
"""

from .address_bits import AddressBitSegment, split_address_bit_segments
from .controller import AddressExplorerController
from .engine import VisualizerStepEngine
from .model import AccessStepViewModel, CacheLineViewModel
from .page_state import AddressExplorerPageState
from .parser import parse_address_trace

__all__ = [
    "AccessStepViewModel",
    "AddressBitSegment",
    "AddressExplorerController",
    "AddressExplorerPageState",
    "CacheLineViewModel",
    "VisualizerStepEngine",
    "parse_address_trace",
    "split_address_bit_segments",
]
