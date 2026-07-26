"""Immutable teaching presets for the M4.1 performance core."""

from dataclasses import dataclass

from cachevis_rv.core import CacheConfig

from .hierarchy import TwoLevelTimingModel
from .model import PerformanceRunSpec
from .sweep import PerformanceSweepDefinition, PerformanceSweepKind
from .timing import PerformanceTimingModel


@dataclass(frozen=True)
class PerformancePreset:
    preset_id: str
    title: str
    description: str
    expected_teaching_conclusion: str
    sweep: PerformanceSweepDefinition | None = None
    hierarchy_model: TwoLevelTimingModel | None = None

    def __post_init__(self) -> None:
        if bool(self.sweep is not None) == bool(self.hierarchy_model is not None):
            raise ValueError("a performance preset must contain one model kind")


STANDARD_TIMING = PerformanceTimingModel(1, 20, 0.5)


def _config(cache_size: int, block_size: int, ways: int, policy: str = "LRU") -> CacheConfig:
    return CacheConfig(
        cache_size_bytes=cache_size,
        block_size_bytes=block_size,
        ways=ways,
        replacement_policy=policy,
    )


def _point(point_id, label, x_value, config, timing=STANDARD_TIMING):
    return PerformanceRunSpec(point_id, label, x_value, config, timing)


CAPACITY_KNEE_SWEEP = PerformanceSweepDefinition(
    sweep_id="capacity_knee",
    title="Capacity Knee",
    description="Fit a four-block working set into progressively larger caches.",
    kind=PerformanceSweepKind.CACHE_SIZE,
    addresses=(0, 4, 8, 12) * 4,
    points=tuple(
        _point(f"cache_{size}", f"{size} B cache", size, _config(size, 4, 1))
        for size in (8, 16, 32)
    ),
    baseline_point_id="cache_8",
    expected_teaching_conclusion=(
        "Once the working set fits, more capacity may not improve this trace; "
        "cache size is not an unconditional performance guarantee."
    ),
)


SEQUENTIAL_BLOCK_BENEFIT_SWEEP = PerformanceSweepDefinition(
    sweep_id="sequential_block_benefit",
    title="Sequential Block Benefit",
    description="Sequential words reuse bytes fetched by larger blocks.",
    kind=PerformanceSweepKind.BLOCK_SIZE,
    addresses=(0, 4, 8, 12, 16, 20, 24, 28),
    points=tuple(
        _point(f"block_{size}", f"{size} B block", size, _config(64, size, 1))
        for size in (4, 8, 16)
    ),
    baseline_point_id="block_4",
    expected_teaching_conclusion=(
        "Larger blocks reduce misses for this sequential trace while increasing "
        "the cost of each fill."
    ),
)


STRIDE_BLOCK_COST_SWEEP = PerformanceSweepDefinition(
    sweep_id="stride_block_cost",
    title="Stride Block Cost",
    description="A 16-byte stride does not consume extra bytes in larger blocks.",
    kind=PerformanceSweepKind.BLOCK_SIZE,
    addresses=(0, 16, 32, 48),
    points=tuple(
        _point(f"block_{size}", f"{size} B block", size, _config(64, size, 1))
        for size in (4, 8, 16)
    ),
    baseline_point_id="block_4",
    expected_teaching_conclusion=(
        "When a stride cannot reuse the extra bytes, larger blocks leave misses "
        "unchanged but increase fill penalty and traffic."
    ),
)


ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP = PerformanceSweepDefinition(
    sweep_id="associativity_conflict_relief",
    title="Associativity Conflict Relief",
    description="Two conflicting blocks can coexist once the target set has two ways.",
    kind=PerformanceSweepKind.ASSOCIATIVITY,
    addresses=(0, 16, 0, 16, 0, 16),
    points=tuple(
        _point(f"ways_{ways}", f"{ways}-way", ways, _config(16, 4, ways))
        for ways in (1, 2, 4)
    ),
    baseline_point_id="ways_1",
    expected_teaching_conclusion=(
        "Associativity can relieve conflicts, but hit-time differences must remain "
        "explicit inputs rather than an assumed formula."
    ),
)


_MISS_CONFIG = _config(16, 4, 2)
MISS_PENALTY_SENSITIVITY_SWEEP = PerformanceSweepDefinition(
    sweep_id="miss_penalty_sensitivity",
    title="Miss Penalty Sensitivity",
    description="Hold cache behavior fixed while changing only miss overhead.",
    kind=PerformanceSweepKind.MISS_PENALTY,
    addresses=(0, 4, 0, 4),
    points=tuple(
        _point(
            f"penalty_{overhead}",
            f"{overhead} cycle miss overhead",
            overhead,
            _MISS_CONFIG,
            PerformanceTimingModel(1, overhead, 0),
        )
        for overhead in (10, 50, 100)
    ),
    baseline_point_id="penalty_10",
    expected_teaching_conclusion=(
        "Identical miss rates can have very different performance when miss penalty changes."
    ),
)


HIT_RATE_IS_NOT_AMAT_SWEEP = PerformanceSweepDefinition(
    sweep_id="hit_rate_is_not_amat",
    title="Hit Rate Is Not AMAT",
    description="Contrast a fast small cache with a slower cache that has more hits.",
    kind=PerformanceSweepKind.CUSTOM,
    addresses=(0, 4, 0, 4),
    points=(
        _point(
            "fast_small",
            "Fast Small",
            0,
            _config(4, 4, 1),
            PerformanceTimingModel(1, 10, 0),
        ),
        _point(
            "slow_large",
            "Slow Large",
            1,
            _config(8, 4, 1),
            PerformanceTimingModel(8, 10, 0),
        ),
    ),
    baseline_point_id="fast_small",
    expected_teaching_conclusion=(
        "Slow Large has a better hit rate but worse AMAT, so hit rate alone is not performance."
    ),
)


ANALYTICAL_L1_L2_MODEL = TwoLevelTimingModel(
    l1_hit_time_cycles=1,
    l1_miss_rate=0.10,
    l2_hit_time_cycles=8,
    l2_local_miss_rate=0.25,
    memory_penalty_cycles=80,
)


PERFORMANCE_PRESETS = (
    PerformancePreset(
        "capacity_knee",
        "Capacity Knee",
        CAPACITY_KNEE_SWEEP.description,
        CAPACITY_KNEE_SWEEP.expected_teaching_conclusion,
        sweep=CAPACITY_KNEE_SWEEP,
    ),
    PerformancePreset(
        "sequential_block_benefit",
        "Sequential Block Benefit",
        SEQUENTIAL_BLOCK_BENEFIT_SWEEP.description,
        SEQUENTIAL_BLOCK_BENEFIT_SWEEP.expected_teaching_conclusion,
        sweep=SEQUENTIAL_BLOCK_BENEFIT_SWEEP,
    ),
    PerformancePreset(
        "stride_block_cost",
        "Stride Block Cost",
        STRIDE_BLOCK_COST_SWEEP.description,
        STRIDE_BLOCK_COST_SWEEP.expected_teaching_conclusion,
        sweep=STRIDE_BLOCK_COST_SWEEP,
    ),
    PerformancePreset(
        "associativity_conflict_relief",
        "Associativity Conflict Relief",
        ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP.description,
        ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP.expected_teaching_conclusion,
        sweep=ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP,
    ),
    PerformancePreset(
        "miss_penalty_sensitivity",
        "Miss Penalty Sensitivity",
        MISS_PENALTY_SENSITIVITY_SWEEP.description,
        MISS_PENALTY_SENSITIVITY_SWEEP.expected_teaching_conclusion,
        sweep=MISS_PENALTY_SENSITIVITY_SWEEP,
    ),
    PerformancePreset(
        "hit_rate_is_not_amat",
        "Hit Rate Is Not AMAT",
        HIT_RATE_IS_NOT_AMAT_SWEEP.description,
        HIT_RATE_IS_NOT_AMAT_SWEEP.expected_teaching_conclusion,
        sweep=HIT_RATE_IS_NOT_AMAT_SWEEP,
    ),
    PerformancePreset(
        "analytical_l1_l2",
        "Analytical L1/L2 Example",
        "Separate L2 local miss rate from its global memory-access probability.",
        (
            "Global memory probability is L1 miss rate multiplied by L2 local miss rate."
        ),
        hierarchy_model=ANALYTICAL_L1_L2_MODEL,
    ),
)

CAPACITY_KNEE = PERFORMANCE_PRESETS[0]
SEQUENTIAL_BLOCK_BENEFIT = PERFORMANCE_PRESETS[1]
STRIDE_BLOCK_COST = PERFORMANCE_PRESETS[2]
ASSOCIATIVITY_CONFLICT_RELIEF = PERFORMANCE_PRESETS[3]
MISS_PENALTY_SENSITIVITY = PERFORMANCE_PRESETS[4]
HIT_RATE_IS_NOT_AMAT = PERFORMANCE_PRESETS[5]
ANALYTICAL_L1_L2_EXAMPLE = PERFORMANCE_PRESETS[6]

PERFORMANCE_SWEEP_PRESETS = tuple(
    preset.sweep for preset in PERFORMANCE_PRESETS if preset.sweep is not None
)


__all__ = [
    "ANALYTICAL_L1_L2_EXAMPLE",
    "ANALYTICAL_L1_L2_MODEL",
    "ASSOCIATIVITY_CONFLICT_RELIEF",
    "ASSOCIATIVITY_CONFLICT_RELIEF_SWEEP",
    "CAPACITY_KNEE",
    "CAPACITY_KNEE_SWEEP",
    "HIT_RATE_IS_NOT_AMAT",
    "HIT_RATE_IS_NOT_AMAT_SWEEP",
    "MISS_PENALTY_SENSITIVITY",
    "MISS_PENALTY_SENSITIVITY_SWEEP",
    "PERFORMANCE_PRESETS",
    "PERFORMANCE_SWEEP_PRESETS",
    "PerformancePreset",
    "SEQUENTIAL_BLOCK_BENEFIT",
    "SEQUENTIAL_BLOCK_BENEFIT_SWEEP",
    "STANDARD_TIMING",
    "STRIDE_BLOCK_COST",
    "STRIDE_BLOCK_COST_SWEEP",
]
