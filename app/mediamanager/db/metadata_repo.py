from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def upsert_media_metadata(
    conn: sqlite3.Connection,
    media_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    now = _utc_now_iso()
    conn.execute(
        """
        INSERT INTO media_metadata (media_id, title, description, notes, updated_at_utc)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(media_id) DO UPDATE SET
          title=excluded.title,
          description=excluded.description,
          notes=excluded.notes,
          updated_at_utc=excluded.updated_at_utc
        """,
        (media_id, title, description, notes, now),
    )
    conn.commit()


def get_media_metadata(conn: sqlite3.Connection, media_id: int) -> Optional[dict]:
    row = conn.execute(
        "SELECT media_id, title, description, notes, updated_at_utc FROM media_metadata WHERE media_id = ?",
        (media_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "media_id": row[0],
        "title": row[1],
        "description": row[2],
        "notes": row[3],
        "updated_at_utc": row[4],
    }
