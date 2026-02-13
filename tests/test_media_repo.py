import sqlite3
import unittest
from pathlib import Path

from app.mediamanager.db.media_repo import add_media_item, list_media_in_scope
from app.mediamanager.db.migrations import init_db


class TestMediaRepo(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        self.db_path = tmp_dir / 'media-repo.db'
        if self.db_path.exists():
            self.db_path.unlink()
        init_db(str(self.db_path))

    def test_add_media_item_normalizes_path(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            media_id = add_media_item(conn, r"C:\\Media\\Cats\\A.JPG", 'image')
            self.assertEqual(media_id, 1)
            rows = conn.execute("SELECT path FROM media_items").fetchall()
            self.assertEqual(rows[0][0], 'c:/media/cats/a.jpg')

    def test_list_media_in_scope_filters_correctly(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            add_media_item(conn, r"C:\\Media\\Cats\\a.jpg", 'image')
            add_media_item(conn, r"C:\\Media\\Dogs\\b.jpg", 'image')
            add_media_item(conn, r"C:\\Elsewhere\\c.jpg", 'image')

            scoped = list_media_in_scope(conn, [r"C:\\Media\\Cats", r"C:\\Media\\Dogs"])
            self.assertEqual([r['path'] for r in scoped], ['c:/media/cats/a.jpg', 'c:/media/dogs/b.jpg'])


if __name__ == '__main__':
    unittest.main()
