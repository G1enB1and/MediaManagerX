# MediaManager

Local-first media asset manager (Phase 1 foundation).

## Current focus
Phase 1: stable viewer + folder scope + persistent metadata.

## Repo layout
- `app/mediamanager/` — Python package code
- `native/` — PySide6 shell integration (planned)
- `server/` — embedded web gallery assets/services (planned)
- `docs/` — architecture + implementation notes
- `scripts/` — dev utilities
- `tests/` — test suite

## Quick start
```bash
cd MediaManager
python3 scripts/init_db.py --db-path ./data/mediamanager.db
```

This initializes schema v1 for persistent catalog + workspace selection state.
