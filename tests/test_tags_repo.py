import sqlite3
import unittest
from pathlib import Path

from app.mediamanager.db.migrations import init_db
from app.mediamanager.db.tags_repo import attach_tags, list_media_tags


class TestTagsRepo(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        self.db_path = tmp_dir / 'tags.db'
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

    def test_attach_and_list_tags(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            attach_tags(conn, 1, ['cat', 'cute'])
            tags = list_media_tags(conn, 1)
        self.assertEqual(tags, ['cat', 'cute'])

    def test_attach_tags_is_idempotent_and_normalized(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            attach_tags(conn, 1, ['cat', 'cat', '  cat  ', ''])
            tags = list_media_tags(conn, 1)
        self.assertEqual(tags, ['cat'])


if __name__ == '__main__':
    unittest.main()
