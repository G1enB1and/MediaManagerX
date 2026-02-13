from __future__ import annotations

from typing import Iterable

from app.mediamanager.utils.pathing import normalize_windows_path


def build_scope_where_clause(selected_roots: Iterable[str]) -> str:
    """Build SQL WHERE predicate for selected folder roots.

    Returns a predicate that matches any media path equal to or under
    one of the selected roots. If no roots are selected, returns "0"
    (always false) for empty gallery behavior.
    """
    roots = sorted({normalize_windows_path(r).rstrip("/") for r in selected_roots if r.strip()})
    if not roots:
        return "0"

    parts: list[str] = []
    for root in roots:
        escaped = root.replace("'", "''")
        parts.append(f"(path = '{escaped}' OR path LIKE '{escaped}/%')")

    return " OR ".join(parts)
