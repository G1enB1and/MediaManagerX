from __future__ import annotations

import sqlite3
from pathlib import Path

from app.mediamanager.db.migrations import init_db


def connect_db(db_path: str) -> sqlite3.Connection:
    """Open a DB connection and ensure schema exists.

    This makes first-run experience seamless: if the database file doesn't
    exist yet, it is created and initialized automatically.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(path))

    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn
