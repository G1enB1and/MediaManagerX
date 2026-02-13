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
make setup
```

That command creates a **brand-new blank database** at `./data/mediamanager.db` if one does not exist, and initializes schema v1.

If you don’t want to use `make`, you can run:
```bash
python3 scripts/setup.py
```

## Smoke run
```bash
make run
```
This launches the current minimal bootstrap entrypoint and confirms the local DB path + initial state.

### Manual alternative (still supported)
```bash
python3 scripts/init_db.py --db-path ./data/mediamanager.db
```

No existing database is required for either command.
