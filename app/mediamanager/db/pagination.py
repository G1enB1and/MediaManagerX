"""Pagination helpers.

UI layers often work in pages (e.g., 100 items/page). Keep the math here so
callers don't re-implement offset calculations differently.
"""

from __future__ import annotations


def page_to_limit_offset(*, page: int, page_size: int) -> tuple[int, int]:
    """Convert a 1-based page number to (limit, offset)."""

    if page <= 0:
        raise ValueError("page must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be > 0")

    limit = int(page_size)
    offset = int((page - 1) * page_size)
    return limit, offset
