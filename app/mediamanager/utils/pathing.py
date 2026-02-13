from __future__ import annotations

from pathlib import PureWindowsPath


def normalize_windows_path(path: str) -> str:
    """Normalize a filesystem path with Windows-friendly semantics.

    - Converts backslashes to slashes
    - Normalizes `.` / `..` using Windows path rules
    - Case-folds for case-insensitive matching
    """
    p = PureWindowsPath(path)
    normalized = p.as_posix()
    return normalized.casefold()


def is_under_root(candidate: str, root: str) -> bool:
    cand = normalize_windows_path(candidate)
    rt = normalize_windows_path(root).rstrip('/')
    return cand == rt or cand.startswith(rt + '/')
