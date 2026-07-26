"""Cache configuration helpers for the core simulator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CacheConfig:
    """Stores cache parameters and derives address split information."""

    cache_size_bytes: int = 8 * 1024
    block_size_bytes: int = 32
    ways: int = 2
    replacement_policy: str = "LRU"
    write_policy: str = "write-through"
    address_bits: int = 32
    write_allocate: bool = True

    def __post_init__(self) -> None:
        """Validate parameters after dataclass initialization."""
        self._require_positive_int("cache_size_bytes", self.cache_size_bytes)
        self._require_positive_int("block_size_bytes", self.block_size_bytes)
        self._require_positive_int("ways", self.ways)
        self._require_positive_int("address_bits", self.address_bits)

        if not self._is_power_of_two(self.cache_size_bytes):
            raise ValueError("cache_size_bytes must be a power of two")
        if not self._is_power_of_two(self.block_size_bytes):
            raise ValueError("block_size_bytes must be a power of two")
        if self.block_size_bytes > self.cache_size_bytes:
            raise ValueError("block_size_bytes must not exceed cache_size_bytes")

        total_lines = self.cache_size_bytes // self.block_size_bytes
        if self.ways > total_lines:
            raise ValueError("ways must not exceed the total number of cache lines")

        set_span = self.block_size_bytes * self.ways
        if self.cache_size_bytes % set_span != 0:
            raise ValueError(
                "cache_size_bytes must be divisible by block_size_bytes * ways"
            )
        if not self._is_power_of_two(self.sets):
            raise ValueError("number of sets must be a power of two")

        allowed_replacement = {"LRU", "FIFO", "Random"}
        if self.replacement_policy not in allowed_replacement:
            raise ValueError(
                f"replacement_policy must be one of {sorted(allowed_replacement)}"
            )

        allowed_write = {"write-through", "write-back"}
        if self.write_policy not in allowed_write:
            raise ValueError(f"write_policy must be one of {sorted(allowed_write)}")
        if not isinstance(self.write_allocate, bool):
            raise ValueError("write_allocate must be a bool")

        if self.tag_bits < 0:
            raise ValueError("address_bits is too small for this cache configuration")

    @property
    def sets(self) -> int:
        """Return the number of cache sets."""
        return self.cache_size_bytes // (self.block_size_bytes * self.ways)

    @property
    def offset_bits(self) -> int:
        """Return the number of block offset bits."""
        return self.block_size_bytes.bit_length() - 1

    @property
    def index_bits(self) -> int:
        """Return the number of set index bits."""
        return self.sets.bit_length() - 1

    @property
    def tag_bits(self) -> int:
        """Return the number of tag bits for the configured address width."""
        return self.address_bits - self.index_bits - self.offset_bits

    @property
    def offset_mask(self) -> int:
        """Return a bit mask for extracting the block offset."""
        return self.block_size_bytes - 1

    @property
    def index_mask(self) -> int:
        """Return a bit mask for extracting the set index."""
        return self.sets - 1

    def split_address(self, address: int) -> dict:
        """Split an integer address into tag, index, and offset."""
        self._require_non_negative_int("address", address)
        offset = address & self.offset_mask
        index = (address >> self.offset_bits) & self.index_mask
        tag = address >> (self.offset_bits + self.index_bits)
        return {"tag": tag, "index": index, "offset": offset}

    @staticmethod
    def _require_positive_int(name: str, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _require_non_negative_int(name: str, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    @staticmethod
    def _is_power_of_two(value: int) -> bool:
        return value > 0 and (value & (value - 1)) == 0
