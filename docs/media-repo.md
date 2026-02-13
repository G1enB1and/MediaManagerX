# Media Repository (Phase 1 foundation)

Initial helper APIs:
- `add_media_item(conn, path, media_type)`
- `list_media_in_scope(conn, selected_roots)`

Behavior:
- Media paths are normalized before persistence.
- Scope listing uses the folder scope query contract from `scope_query.py`.
- Current output fields: `id`, `path`, `media_type`.
