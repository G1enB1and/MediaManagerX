#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mediamanager.db.migrations import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize MediaManager database schema")
    parser.add_argument("--db-path", required=True, help="Path to sqlite database file")
    args = parser.parse_args()

    init_db(args.db_path)
    print(f"Initialized MediaManager DB at: {args.db_path}")


if __name__ == "__main__":
    main()
