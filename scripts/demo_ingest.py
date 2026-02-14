#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mediamanager.db.connect import connect_db
from app.mediamanager.db.repository import MediaRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: ingest a few media paths and list scoped results")
    parser.add_argument("--db-path", default="data/mediamanager.db")
    parser.add_argument("--select", action="append", default=[], help="Folder root to select (repeatable)")
    parser.add_argument("--add", action="append", default=[], help="Media file path to ingest (repeatable)")
    args = parser.parse_args()

    conn = connect_db(args.db_path)
    repo = MediaRepository(conn)

    for p in args.add:
        # naive type inference for demo only
        lower = p.lower()
        media_type = "video" if lower.endswith((".mp4", ".webm", ".mkv")) else "gif" if lower.endswith(".gif") else "image"
        repo.ingest_media(p, media_type)

    if args.select:
        repo.set_selection(args.select)

    items = repo.scoped_media()
    print(f"Selected roots: {repo.current_selection()}")
    print(f"Items in scope: {len(items)}")
    for it in items[:20]:
        print(f"- [{it['media_type']}] {it['path']}")

    conn.close()


if __name__ == "__main__":
    main()
