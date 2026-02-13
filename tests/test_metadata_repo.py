import sqlite3
import unittest
from pathlib import Path

from app.mediamanager.db.migrations import init_db
from app.mediamanager.db.metadata_repo import get_media_metadata, upsert_media_metadata


class TestMetadataRepo(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        self.db_path = tmp_dir / 'metadata.db'
        if self.db_path.exists():
            self.db_path.unlink()
        init_db(str(self.db_path))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO media_items (
                  path, media_type, created_at_utc, updated_at_utc
                ) VALUES (?, ?, datetime('now'), datetime('now'))
                """,
                ('c:/media/cats/a.jpg', 'image'),
            )
            conn.commit()

    def test_upsert_and_read_metadata(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            upsert_media_metadata(conn, 1, title='A', description='B', notes='C')
            data = get_media_metadata(conn, 1)

        self.assertIsNotNone(data)
        assert data is not None
        self.assertEqual(data['title'], 'A')
        self.assertEqual(data['description'], 'B')
        self.assertEqual(data['notes'], 'C')

    def test_upsert_overwrites_existing_row(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            upsert_media_metadata(conn, 1, title='Old')
            upsert_media_metadata(conn, 1, title='New', notes='Note')
            data = get_media_metadata(conn, 1)

        self.assertIsNotNone(data)
        assert data is not None
        self.assertEqual(data['title'], 'New')
        self.assertEqual(data['notes'], 'Note')


if __name__ == '__main__':
    unittest.main()
