# App Bootstrap (Phase 1 foundation)

Added `app/mediamanager/main.py` with:
- `bootstrap_repository(db_path="data/mediamanager.db")`
- `run_cli_smoke(db_path=...)`
- CLI entrypoint args (`--db-path`) for custom local DB locations

Purpose:
- Establish a minimal app entry seam that auto-initializes the local DB and returns a ready `MediaRepository`.
- Provide a tiny smoke runnable while native UI wiring is still in progress.
