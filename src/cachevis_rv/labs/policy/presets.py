"""Deterministic teaching presets for replacement-policy comparison."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig


@dataclass(frozen=True)
class PolicyPreset:
    preset_id: str
    title: str
    description: str
    config: CacheConfig
    addresses: tuple[int, ...]
    random_seed: int
    expected_teaching_conclusion: str
    expected_lru_hits: int
    expected_lru_misses: int
    expected_fifo_hits: int
    expected_fifo_misses: int


def _config(cache_size: int, ways: int) -> CacheConfig:
    return CacheConfig(
        cache_size_bytes=cache_size,
        block_size_bytes=1,
        ways=ways,
        replacement_policy="LRU",
    )


NO_REPLACEMENT_PRESSURE = PolicyPreset(
    "no_replacement_pressure",
    "No Replacement Pressure",
    "Two blocks fit, so misses use invalid lines and later accesses hit.",
    _config(2, 2),
    (0, 1, 0, 1),
    2026,
    "Without a full-set miss, replacement policy does not choose a victim.",
    2, 2, 2, 2,
)

VICTIM_DIVERGENCE_BEFORE_OUTCOME = PolicyPreset(
    "victim_divergence_before_outcome",
    "Victim Divergence Before Outcome",
    "A hit refreshes LRU recency but not FIFO insertion order before eviction.",
    _config(2, 2),
    (0, 1, 0, 2),
    2026,
    "Policies can diverge in victim and state before hit/miss outcomes diverge.",
    1, 3, 1, 3,
)

LRU_ADVANTAGE = PolicyPreset(
    "lru_advantage",
    "LRU Advantage",
    "Revisit block 0 after LRU protects it and FIFO evicts it.",
    _config(2, 2),
    (0, 1, 0, 2, 0),
    2026,
    "LRU's recency update preserves block 0 for the final access.",
    2, 3, 1, 4,
)

FIFO_ADVANTAGE = PolicyPreset(
    "fifo_advantage",
    "FIFO Advantage",
    "Revisit block 1 after FIFO preserves it and LRU evicts it.",
    _config(2, 2),
    (0, 1, 0, 2, 1),
    2026,
    "LRU is not guaranteed to outperform FIFO on every finite trace.",
    1, 4, 2, 3,
)

SET_LOCAL_PRESSURE = PolicyPreset(
    "set_local_pressure",
    "Set-Local Pressure",
    "All accessed blocks map to set 0 while the other set remains unused.",
    _config(4, 2),
    (0, 2, 0, 4, 2),
    2026,
    "Victim selection is local to the indexed set, not the whole cache.",
    1, 4, 2, 3,
)

DIRECT_MAPPED_CONTROL = PolicyPreset(
    "direct_mapped_control",
    "Direct-Mapped Control",
    "One way per set leaves no replacement choice.",
    _config(4, 1),
    (0, 4, 0, 4),
    2026,
    "Policy names cannot change the sole victim in a direct-mapped cache.",
    0, 4, 0, 4,
)

SEEDED_RANDOM_REPLAY = PolicyPreset(
    "seeded_random_replay",
    "Seeded Random Replay",
    "Exercise reproducible Random replacement without asserting one fragile sequence.",
    _config(2, 2),
    (0, 1, 2, 0, 3, 1, 4, 0),
    2026,
    "The Random lane is reproducible and every victim remains a valid candidate.",
    0, 8, 0, 8,
)

POLICY_PRESETS = (
    NO_REPLACEMENT_PRESSURE,
    VICTIM_DIVERGENCE_BEFORE_OUTCOME,
    LRU_ADVANTAGE,
    FIFO_ADVANTAGE,
    SET_LOCAL_PRESSURE,
    DIRECT_MAPPED_CONTROL,
    SEEDED_RANDOM_REPLAY,
)


__all__ = [
    "PolicyPreset",
    "NO_REPLACEMENT_PRESSURE",
    "VICTIM_DIVERGENCE_BEFORE_OUTCOME",
    "LRU_ADVANTAGE",
    "FIFO_ADVANTAGE",
    "SET_LOCAL_PRESSURE",
    "DIRECT_MAPPED_CONTROL",
    "SEEDED_RANDOM_REPLAY",
    "POLICY_PRESETS",
]
