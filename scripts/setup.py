#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mediamanager.db.connect import connect_db


def main() -> None:
    db_path = Path("data/mediamanager.db")
    conn = connect_db(str(db_path))
    conn.close()
    print(f"✅ MediaManager is initialized. Blank database ready at: {db_path}")


if __name__ == "__main__":
    main()
