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
python3 scripts/setup.py
```

That single command creates a **brand-new blank database** at `./data/mediamanager.db` if one does not exist, and initializes schema v1.

(Convenience alias: `make setup` runs the same setup script.)

## Smoke run
```bash
make run
```
This launches the current minimal bootstrap entrypoint and confirms the local DB path + initial state.

## Tests / validation
```bash
make test
```
Runs `scripts/dev_check.py` (unit tests + basic sanity checks). Use `python3` explicitly (this repo assumes `python3`, not `python`).

No existing database is required.
