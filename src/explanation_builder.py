"""Build human-readable explanations for visualized cache accesses."""

from cache_config import CacheConfig
from visualizer_model import CacheLineViewModel


def build_explanation_lines(
    config: CacheConfig,
    *,
    address: int,
    tag: int,
    index: int,
    offset: int,
    hit: bool,
    hit_way: int | None,
    victim_way: int | None,
    replaced_valid: bool,
    replaced_tag: int | None,
    replacement_reason: str | None,
    miss_type: str | None,
    before_set_lines: list[CacheLineViewModel],
) -> list[str]:
    """Return explanation lines for the current cache access."""
    lines = [
        (
            f"Offset uses {config.offset_bits} bit(s) because block size is "
            f"{config.block_size_bytes} byte(s), and log2(block size) = "
            f"{config.offset_bits}."
        ),
        (
            f"Index uses {config.index_bits} bit(s) because the cache has "
            f"{config.sets} set(s), and log2(sets) = {config.index_bits}."
        ),
        (
            f"Tag uses the remaining high bits: {config.address_bits} - "
            f"{config.index_bits} - {config.offset_bits} = {config.tag_bits}."
        ),
        (
            "Teaching view: Index selects the cache set/row, Offset selects "
            "the byte or word position inside the block, and Tag is the "
            "remaining high part used to check whether this is the target "
            "memory block."
        ),
        (
            f"Address {address} splits into tag={tag}, index={index}, "
            f"offset={offset}, so it maps to set {index}."
        ),
    ]

    if hit:
        lines.append(
            f"Way {hit_way} in set {index} has valid=1 and matching tag={tag} "
            "(valid bit is 1, and the stored tag matches the requested tag); "
            "therefore this access is a cache hit."
        )
        return lines

    lines.append(
        "No line in the mapped set has both valid bit = 1 and a matching tag, "
        "so this access is a cache miss."
    )
    if miss_type == "compulsory":
        lines.append(
            "This miss is compulsory because it is the first access to this "
            "memory block in the trace."
        )
    elif miss_type:
        lines.append(f"Miss type is currently classified as {miss_type}.")
    else:
        lines.append("Miss type is reserved for later classification.")

    if replacement_reason == "invalid-line":
        lines.append(
            f"Way {victim_way} is invalid before the access, so the cache fills "
            "that invalid line first instead of evicting a valid block."
        )
    elif replaced_valid:
        lines.append(
            f"All candidate lines were valid, so {config.replacement_policy} "
            f"selects way {victim_way} as the victim."
        )
        lines.append(f"The replaced tag is {replaced_tag}.")
    elif victim_way is not None:
        lines.append(f"The new block is placed in way {victim_way}.")

    if before_set_lines:
        valid_tags = [
            f"way {line.way_index}: tag={line.tag}"
            for line in before_set_lines
            if line.valid
        ]
        if valid_tags:
            lines.append("Before this access, valid tags in the set were: " + ", ".join(valid_tags) + ".")
        else:
            lines.append("Before this access, the mapped set had no valid lines.")

    return lines
