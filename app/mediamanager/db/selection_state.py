from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Iterable, List

from app.mediamanager.utils.pathing import normalize_windows_path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def replace_selection(conn: sqlite3.Connection, selected_roots: Iterable[str]) -> None:
    """Replace folder_selection_state with normalized unique roots."""
    roots = sorted({normalize_windows_path(r).rstrip("/") for r in selected_roots if r.strip()})
    now = _utc_now_iso()

    conn.execute("DELETE FROM folder_selection_state")
    conn.executemany(
        "INSERT INTO folder_selection_state(path, selected_at_utc) VALUES (?, ?)",
        [(root, now) for root in roots],
    )
    conn.commit()


def get_selection(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT path FROM folder_selection_state ORDER BY path"
    ).fetchall()
    return [row[0] for row in rows]
