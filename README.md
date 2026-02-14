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

## Status
This repo is currently **Phase 1 foundation** (DB + repository layer + tests + a tiny CLI smoke runner).

There is **no GUI you can “open” yet**—that comes later when we wire in the native shell + viewer.

## Quick start (no `make` required)
```bash
git clone https://github.com/G1enB1and/MediaManagerX.git
cd MediaManagerX

# optional but recommended: create a venv
python3 -m venv .venv
source .venv/bin/activate

# install in editable mode
pip install -e .

# one command: creates/initializes the DB (default: ./data/mediamanager.db)
python3 scripts/setup.py
```

## Run (current smoke CLI)
```bash
python3 app/mediamanager/main.py
# or
python3 -m app.mediamanager.main
```

You should see output like:
- `MediaManager ready`
- `DB: .../data/mediamanager.db`

## If you *do* want `make`
On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install make
```
Then these convenience targets work:
- `make setup` → runs `python3 scripts/setup.py`
- `make run` → runs the smoke CLI
- `make test` → runs `python3 scripts/dev_check.py`

## Tests / validation (no `make` required)
```bash
python3 scripts/dev_check.py
```
