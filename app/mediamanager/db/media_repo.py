from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List

from app.mediamanager.db.scope_query import build_scope_where
from app.mediamanager.utils.pathing import normalize_windows_path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_media_item(conn: sqlite3.Connection, path: str, media_type: str) -> int:
    now = _utc_now_iso()
    normalized = normalize_windows_path(path)
    conn.execute(
        """
        INSERT INTO media_items(path, media_type, created_at_utc, updated_at_utc)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
          media_type=excluded.media_type,
          updated_at_utc=excluded.updated_at_utc
        """,
        (normalized, media_type, now, now),
    )
    row = conn.execute("SELECT id FROM media_items WHERE path = ?", (normalized,)).fetchone()
    if not row:
        raise RuntimeError("failed to insert media item")
    conn.commit()
    return int(row[0])


def list_media_in_scope(conn: sqlite3.Connection, selected_roots: list[str]) -> List[dict]:
    where_sql, params = build_scope_where(selected_roots)
    rows = conn.execute(
        f"SELECT id, path, media_type FROM media_items WHERE {where_sql} ORDER BY path",
        params,
    ).fetchall()
    return [{"id": r[0], "path": r[1], "media_type": r[2]} for r in rows]
