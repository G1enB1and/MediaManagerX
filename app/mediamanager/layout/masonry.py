"""Masonry layout (container-first) helpers.

This module is intentionally UI-framework agnostic.

Goal: given a *known* container width and a list of media items with an
aspect ratio (or a fallback height), compute stable positions without
waiting for assets to load.

UI layers (web/Qt) can later reconcile with actual decoded dimensions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class MasonryItem:
    """Input item for layout.

    aspect_ratio: width / height. If unknown, provide fallback_height_px.
    """

    key: str
    aspect_ratio: Optional[float] = None
    fallback_height_px: int = 200


@dataclass(frozen=True)
class MasonryPlacement:
    key: str
    column: int
    x: int
    y: int
    width: int
    height: int


def _column_width(container_width_px: int, columns: int, gutter_px: int) -> int:
    if columns <= 0:
        raise ValueError("columns must be > 0")
    if container_width_px <= 0:
        raise ValueError("container_width_px must be > 0")
    if gutter_px < 0:
        raise ValueError("gutter_px must be >= 0")

    usable = container_width_px - gutter_px * (columns - 1)
    if usable <= 0:
        raise ValueError("container too small for given columns/gutter")

    # Int math is fine; UI can subpixel later if needed.
    return usable // columns


def layout_masonry(
    *,
    container_width_px: int,
    columns: int,
    gutter_px: int,
    items: Iterable[MasonryItem],
) -> Tuple[List[MasonryPlacement], int]:
    """Compute placements and total height.

    Algorithm: greedy assignment to shortest column.

    Returns (placements, total_height_px).
    """

    col_w = _column_width(container_width_px, columns, gutter_px)
    col_heights = [0 for _ in range(columns)]

    placements: List[MasonryPlacement] = []
    for item in items:
        # Select shortest column (stable: choose lowest index on ties).
        col = min(range(columns), key=lambda c: col_heights[c])
        x = col * (col_w + gutter_px)
        y = col_heights[col]

        if item.aspect_ratio and item.aspect_ratio > 0:
            h = max(1, int(round(col_w / item.aspect_ratio)))
        else:
            h = max(1, int(item.fallback_height_px))

        placements.append(
            MasonryPlacement(
                key=item.key,
                column=col,
                x=int(x),
                y=int(y),
                width=int(col_w),
                height=int(h),
            )
        )

        col_heights[col] = y + h + gutter_px

    total = max(col_heights) - (gutter_px if placements else 0)
    total = max(0, int(total))
    return placements, total
