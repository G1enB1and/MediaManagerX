from __future__ import annotations

from pathlib import Path
import argparse

from app.mediamanager.db.connect import connect_db
from app.mediamanager.db.repository import MediaRepository


def bootstrap_repository(db_path: str = "data/mediamanager.db") -> MediaRepository:
    conn = connect_db(db_path)
    return MediaRepository(conn)


def run_cli_smoke(db_path: str = "data/mediamanager.db") -> None:
    repo = bootstrap_repository(db_path)
    selection = repo.current_selection()
    print("MediaManager ready")
    print(f"DB: {Path(db_path).resolve()}")
    print(f"Current selection roots: {len(selection)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="MediaManager bootstrap smoke runner")
    parser.add_argument("--db-path", default="data/mediamanager.db", help="SQLite DB path")
    args = parser.parse_args()
    run_cli_smoke(args.db_path)


if __name__ == "__main__":
    main()
