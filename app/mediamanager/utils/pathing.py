from __future__ import annotations

from pathlib import Path


def normalize_windows_path(path: str) -> str:
    """Normalize a filesystem path with Windows-friendly semantics.

    - Converts backslashes to slashes
    - Normalizes `.` / `..`
    - Case-folds drive letters and path for case-insensitive matching
    """
    p = Path(path)
    normalized = str(p).replace('\\', '/')
    return normalized.casefold()


def is_under_root(candidate: str, root: str) -> bool:
    cand = normalize_windows_path(candidate)
    rt = normalize_windows_path(root).rstrip('/')
    return cand == rt or cand.startswith(rt + '/')
