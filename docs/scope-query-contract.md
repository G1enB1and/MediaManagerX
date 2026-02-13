# Scope Query Contract (Phase 1)

`build_scope_where_clause(selected_roots)` generates SQL predicate text for gallery filtering.

Rules:
- Empty selection -> `0` (always false, empty gallery)
- For each selected root `r` -> `(path = r OR path LIKE r/%)`
- Inputs are normalized to Windows-safe lowercase slash form
- Duplicate roots are removed before predicate generation

This keeps selection-scope logic explicit and testable before wiring DB query execution.
