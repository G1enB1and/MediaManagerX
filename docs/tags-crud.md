# Tags CRUD (Phase 1 foundation)

Initial helper APIs:
- `get_or_create_tag(conn, name, category=None)`
- `attach_tags(conn, media_id, tag_names)`
- `list_media_tags(conn, media_id)`

Behavior:
- Tag names are deduped/trimmed per call
- Tag rows are created lazily
- `media_tags` inserts are idempotent via `(media_id, tag_id)` primary key
