# Scope Query Contract (Phase 1)

`build_scope_where(selected_roots)` generates a **parameterized** SQL predicate for gallery filtering.

Rules:
- Empty selection -> `( "0", [] )` (always false, empty gallery)
- For each selected root `r` -> `(path = ? OR path LIKE ?)` with params `[r, r + "/%"]`
- Inputs are normalized to Windows-safe lowercase slash form
- Duplicate roots are removed before predicate generation

A debug helper `build_scope_where_clause(...)` still exists for readable strings, but DB code should use `build_scope_where(...)`.
