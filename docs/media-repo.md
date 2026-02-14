# Media Repository (Phase 1 foundation)

Initial helper APIs:
- `add_media_item(conn, path, media_type)`
- `list_media_in_scope(conn, selected_roots, limit=None, offset=None)`

Behavior:
- Media paths are normalized before persistence.
- Scope listing uses the folder scope query contract from `scope_query.py`.
- Supports pagination with `limit`/`offset`.
- Current output fields: `id`, `path`, `media_type`.
