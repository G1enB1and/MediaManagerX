# Repository Facade (Phase 1 foundation)

Added `MediaRepository` (`app/mediamanager/db/repository.py`) as a thin orchestrating wrapper around current DB helper modules.

Purpose:
- Provide a single integration seam for upcoming native UI wiring.
- Keep helper modules composable/testable while exposing straightforward app-level operations.

Covered operations:
- ingest media
- set/get selection
- query scoped media
- save/load metadata
- add/list tags
