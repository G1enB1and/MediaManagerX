# Selection State (Phase 1)

`folder_selection_state` stores only current gallery scope roots.

Current helper APIs:
- `replace_selection(conn, selected_roots)` — clears and replaces selected roots with normalized unique paths.
- `get_selection(conn)` — returns current selected roots sorted.

Invariant reminder:
- Updating/clearing selection state must never modify persistent metadata tables.
