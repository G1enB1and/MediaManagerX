# Phase 1 Foundation Notes

## Embedded web strategy
Locked: `PySide6.QWebEngineView` for initial build.

Reasoning:
- First-party in Qt stack
- Stable integration path for local desktop shell
- Good enough for local embedded gallery while keeping architecture modular

## Completed in this step
- Project scaffold directories
- Windows-safe path normalization utility (now using `PureWindowsPath.as_posix()` to avoid duplicate slashes)
- SQLite schema v1 bootstrap + init script
- Basic unit tests for path normalization/scope checks and DB bootstrap table creation
