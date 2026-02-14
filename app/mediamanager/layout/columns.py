"""Responsive column-count helpers for masonry layouts."""

from __future__ import annotations


def choose_columns(
    *,
    container_width_px: int,
    min_column_width_px: int,
    gutter_px: int,
    max_columns: int = 12,
) -> int:
    """Choose a reasonable column count.

    Policy:
    - columns >= 1
    - each column should be at least min_column_width_px
    - account for gutters between columns
    - clamp to max_columns

    This is intentionally simple; UI layers may override with breakpoints.
    """

    if container_width_px <= 0:
        raise ValueError("container_width_px must be > 0")
    if min_column_width_px <= 0:
        raise ValueError("min_column_width_px must be > 0")
    if gutter_px < 0:
        raise ValueError("gutter_px must be >= 0")
    if max_columns <= 0:
        raise ValueError("max_columns must be > 0")

    # We want the largest N such that:
    # N*min + (N-1)*gutter <= container
    # => N*(min+gutter) - gutter <= container
    # => N <= (container+gutter)/(min+gutter)
    denom = min_column_width_px + gutter_px
    n = (container_width_px + gutter_px) // denom
    n = int(max(1, min(max_columns, n)))
    return n
