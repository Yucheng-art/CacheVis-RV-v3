"""Single-step cache simulation engine for the visualizer logic layer."""

from cache_config import CacheConfig
from cache_simulator import CacheSimulator
from explanation_builder import build_explanation_lines
from visualizer_model import AccessStepViewModel, CacheLineViewModel


class VisualizerStepEngine:
    """Run a cache trace one address at a time and return view models."""

    def __init__(self, config: CacheConfig, addresses: list[int]) -> None:
        if not addresses:
            raise ValueError("addresses must not be empty")
        self.config = config
        self.addresses = list(addresses)
        self.simulator = CacheSimulator(config)
        self.current_step = 0
        self._seen_memory_blocks: set[int] = set()

    def reset(self) -> None:
        """Reset simulator state and rewind the trace."""
        self.simulator.reset()
        self.current_step = 0
        self._seen_memory_blocks.clear()

    def has_next(self) -> bool:
        """Return whether another address can be stepped."""
        return self.current_step < len(self.addresses)

    def step(self) -> AccessStepViewModel:
        """Execute one address access and return all data needed by the GUI."""
        if not self.has_next():
            raise StopIteration("no more addresses to step")

        address = self.addresses[self.current_step]
        parts = self.config.split_address(address)
        mapped_set = parts["index"]
        before_snapshot = self.simulator.get_cache_snapshot()
        before_set_lines = _line_models_from_set(before_snapshot[mapped_set])
        memory_block = address // self.config.block_size_bytes
        first_block_access = memory_block not in self._seen_memory_blocks

        access_result = self.simulator.access(address)
        self._seen_memory_blocks.add(memory_block)

        after_snapshot = _snapshot_to_line_models(self.simulator.get_cache_snapshot())
        stats = self.simulator.get_statistics()
        hit = bool(access_result["hit"])
        hit_way = access_result["victim_way"] if hit else None
        victim_way = None if hit else access_result["victim_way"]
        replacement_reason = None if hit else _replacement_reason(
            before_set_lines,
            victim_way,
            self.config.replacement_policy,
        )
        miss_type = None
        if not hit:
            miss_type = "compulsory" if first_block_access else "unknown"

        explanation_lines = build_explanation_lines(
            self.config,
            address=address,
            tag=parts["tag"],
            index=parts["index"],
            offset=parts["offset"],
            hit=hit,
            hit_way=hit_way,
            victim_way=victim_way,
            replaced_valid=bool(access_result["replaced_valid"]),
            replaced_tag=access_result["replaced_tag"],
            replacement_reason=replacement_reason,
            miss_type=miss_type,
            before_set_lines=before_set_lines,
        )

        view_model = AccessStepViewModel(
            step_index=self.current_step,
            address=address,
            address_dec=str(address),
            address_hex=f"0x{address:08x}",
            address_binary=_format_binary(address, self.config.address_bits),
            tag_bits=self.config.tag_bits,
            index_bits=self.config.index_bits,
            offset_bits=self.config.offset_bits,
            tag=parts["tag"],
            index=parts["index"],
            offset=parts["offset"],
            mapped_set=mapped_set,
            hit=hit,
            hit_way=hit_way,
            victim_way=victim_way,
            replaced_valid=bool(access_result["replaced_valid"]),
            replaced_tag=access_result["replaced_tag"],
            replacement_reason=replacement_reason,
            miss_type=miss_type,
            before_set_lines=before_set_lines,
            after_cache_snapshot=after_snapshot,
            total_accesses=int(stats["total_accesses"]),
            hits=int(stats["hits"]),
            misses=int(stats["misses"]),
            hit_rate=float(stats["hit_rate"]),
            miss_rate=float(stats["miss_rate"]),
            explanation_lines=explanation_lines,
        )
        self.current_step += 1
        return view_model


def _format_binary(address: int, address_bits: int) -> str:
    return format(address, f"0{address_bits}b")


def _replacement_reason(
    before_set_lines: list[CacheLineViewModel],
    victim_way: int | None,
    policy: str,
) -> str | None:
    if victim_way is None:
        return None
    victim_before = next(
        (line for line in before_set_lines if line.way_index == victim_way),
        None,
    )
    if victim_before is not None and not victim_before.valid:
        return "invalid-line"
    return policy


def _snapshot_to_line_models(snapshot: list[list[dict]]) -> list[list[CacheLineViewModel]]:
    return [_line_models_from_set(cache_set) for cache_set in snapshot]


def _line_models_from_set(cache_set: list[dict]) -> list[CacheLineViewModel]:
    return [
        CacheLineViewModel(
            set_index=int(line["set_index"]),
            way_index=int(line["way"]),
            valid=bool(line["valid"]),
            tag=line["tag"],
            dirty=bool(line["dirty"]),
            last_used=int(line["last_used"]),
            insert_time=int(line["insert_time"]),
        )
        for line in cache_set
    ]
