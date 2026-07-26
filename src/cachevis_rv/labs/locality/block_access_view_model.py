"""Executed-trace block/offset aggregation for Locality Lab."""

from dataclasses import dataclass

from .model import LocalityKind, LocalityStep


@dataclass(frozen=True)
class BlockAccessCellViewModel:
    block_address: int
    offset: int
    address: int
    access_count: int
    hit_count: int
    miss_count: int
    first_touch_count: int
    spatial_count: int
    temporal_count: int
    first_step: int
    last_step: int
    is_current_address: bool
    is_current_block: bool


@dataclass(frozen=True)
class BlockAccessSummaryViewModel:
    block_address: int
    total_accesses: int
    unique_offsets: int
    hit_count: int
    miss_count: int
    first_step: int
    last_step: int


def build_block_access_models(
    steps: tuple[LocalityStep, ...],
    current_step: LocalityStep | None = None,
) -> tuple[
    tuple[BlockAccessCellViewModel, ...],
    tuple[BlockAccessSummaryViewModel, ...],
]:
    """Aggregate only already executed steps; never inspect future addresses."""
    cells: dict[tuple[int, int, int], list[LocalityStep]] = {}
    blocks: dict[int, list[LocalityStep]] = {}
    for step in steps:
        cells.setdefault(
            (step.block_address, step.offset, step.address), []
        ).append(step)
        blocks.setdefault(step.block_address, []).append(step)

    cell_models = tuple(
        BlockAccessCellViewModel(
            block_address=block,
            offset=offset,
            address=address,
            access_count=len(group),
            hit_count=sum(step.cache_hit for step in group),
            miss_count=sum(not step.cache_hit for step in group),
            first_touch_count=sum(
                step.locality_kind is LocalityKind.FIRST_TOUCH for step in group
            ),
            spatial_count=sum(
                step.locality_kind is LocalityKind.SPATIAL for step in group
            ),
            temporal_count=sum(
                step.locality_kind is LocalityKind.TEMPORAL for step in group
            ),
            first_step=group[0].step_index,
            last_step=group[-1].step_index,
            is_current_address=(
                current_step is not None and address == current_step.address
            ),
            is_current_block=(
                current_step is not None and block == current_step.block_address
            ),
        )
        for (block, offset, address), group in sorted(cells.items())
    )
    summaries = tuple(
        BlockAccessSummaryViewModel(
            block_address=block,
            total_accesses=len(group),
            unique_offsets=len({step.offset for step in group}),
            hit_count=sum(step.cache_hit for step in group),
            miss_count=sum(not step.cache_hit for step in group),
            first_step=group[0].step_index,
            last_step=group[-1].step_index,
        )
        for block, group in sorted(blocks.items())
    )
    return cell_models, summaries


__all__ = [
    "BlockAccessCellViewModel",
    "BlockAccessSummaryViewModel",
    "build_block_access_models",
]
