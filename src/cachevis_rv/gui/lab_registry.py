"""Read-only metadata registry for available and future CacheVis-RV labs."""

from dataclasses import dataclass
from typing import Callable


AVAILABLE = "Available"
COMING_SOON = "Coming Soon"
LabFactory = Callable[[], object]


@dataclass(frozen=True)
class LabDefinition:
    """Metadata and optional lazy factory for one platform lab."""

    lab_id: str
    title: str
    short_title: str
    description: str
    category: str
    status: str
    concepts: tuple[str, ...]
    factory: LabFactory | None
    order: int


def _create_address_explorer():
    from cachevis_rv.labs.address_explorer.widget import AddressVisualizerWidget

    return AddressVisualizerWidget()


def _create_miss_type():
    from cachevis_rv.labs.miss_type.widget import MissTypeLabWidget

    return MissTypeLabWidget()


def _create_locality():
    from cachevis_rv.labs.locality.widget import LocalityLabWidget

    return LocalityLabWidget()


def _create_policy():
    from cachevis_rv.labs.policy.widget import PolicyLabWidget

    return PolicyLabWidget()


def _create_single_experiment():
    from cachevis_rv.labs.single_experiment import SingleExperimentWidget

    return SingleExperimentWidget()


def _create_compare_experiment():
    from cachevis_rv.labs.compare_experiment import CompareExperimentWidget

    return CompareExperimentWidget()


LAB_REGISTRY = (
    LabDefinition(
        lab_id="address_explorer",
        title="Address Explorer",
        short_title="Address Explorer",
        description="Step through addresses to see tag, index, offset, and cache-line updates.",
        category="Learn",
        status=AVAILABLE,
        concepts=("Address split", "Cache mapping", "Hit / miss"),
        factory=_create_address_explorer,
        order=10,
    ),
    LabDefinition(
        lab_id="miss_type",
        title="Miss Type Lab",
        short_title="Miss Types",
        description="Explore compulsory, conflict, and capacity misses with guided traces.",
        category="Learn",
        status=AVAILABLE,
        concepts=("3C model", "Miss classification"),
        factory=_create_miss_type,
        order=20,
    ),
    LabDefinition(
        lab_id="locality",
        title="Locality Lab",
        short_title="Locality",
        description="Relate temporal and spatial locality to cache behavior.",
        category="Learn",
        status=AVAILABLE,
        concepts=("Temporal locality", "Spatial locality"),
        factory=_create_locality,
        order=30,
    ),
    LabDefinition(
        lab_id="policy",
        title="Policy Lab",
        short_title="Policies",
        description="Compare how replacement choices affect cache contents over time.",
        category="Learn",
        status=AVAILABLE,
        concepts=("LRU", "FIFO", "Random"),
        factory=_create_policy,
        order=40,
    ),
    LabDefinition(
        lab_id="performance",
        title="Performance Lab",
        short_title="Performance",
        description="Connect hit rate and miss cost to effective memory performance.",
        category="Learn",
        status=COMING_SOON,
        concepts=("AMAT", "Miss penalty"),
        factory=None,
        order=50,
    ),
    LabDefinition(
        lab_id="write_policy",
        title="Write Policy Lab",
        short_title="Write Policy",
        description="Study write-through, write-back, allocation, and dirty data.",
        category="Learn",
        status=COMING_SOON,
        concepts=("Write-through", "Write-back"),
        factory=None,
        order=60,
    ),
    LabDefinition(
        lab_id="single_experiment",
        title="Single Experiment",
        short_title="Single Experiment",
        description="Run one configurable cache experiment and export its results.",
        category="Classic Tools",
        status=AVAILABLE,
        concepts=("Trace generation", "Statistics", "Reports"),
        factory=_create_single_experiment,
        order=70,
    ),
    LabDefinition(
        lab_id="compare_experiment",
        title="Compare Experiment",
        short_title="Compare Experiment",
        description="Compare associativity, block size, or cache size side by side.",
        category="Classic Tools",
        status=AVAILABLE,
        concepts=("Parameter comparison", "Trade-offs"),
        factory=_create_compare_experiment,
        order=80,
    ),
)

_LABS_BY_ID = {lab.lab_id: lab for lab in LAB_REGISTRY}


def get_lab(lab_id: str) -> LabDefinition | None:
    """Return one lab definition without constructing its page."""
    return _LABS_BY_ID.get(lab_id)


def get_labs() -> tuple[LabDefinition, ...]:
    """Return all definitions in stable product order."""
    return LAB_REGISTRY


def get_available_labs() -> tuple[LabDefinition, ...]:
    """Return navigable labs in stable product order."""
    return tuple(lab for lab in LAB_REGISTRY if lab.status == AVAILABLE)


__all__ = [
    "AVAILABLE",
    "COMING_SOON",
    "LAB_REGISTRY",
    "LabDefinition",
    "get_available_labs",
    "get_lab",
    "get_labs",
]
