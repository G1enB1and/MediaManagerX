# Metadata CRUD (Phase 1 foundation)

Initial repository helpers added:
- `upsert_media_metadata(conn, media_id, title, description, notes)`
- `get_media_metadata(conn, media_id)`

Current behavior:
- Uses SQL upsert keyed by `media_id`
- Updates `updated_at_utc` on each write
- Keeps metadata in persistent table independent of folder selection state
