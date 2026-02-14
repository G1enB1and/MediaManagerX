import unittest
from pathlib import Path

from app.mediamanager.db.connect import connect_db
from app.mediamanager.db.media_repo import add_media_item, list_media_in_scope


class TestMediaRepoPagination(unittest.TestCase):
    def test_limit_offset_paginates_in_path_order(self):
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        db_path = tmp_dir / 'pagination-media-repo.db'
        if db_path.exists():
            db_path.unlink()

        conn = connect_db(str(db_path))

        # Insert out of order to ensure ORDER BY path drives pagination
        add_media_item(conn, r"C:\Media\b.png", "image")
        add_media_item(conn, r"C:\Media\a.png", "image")
        add_media_item(conn, r"C:\Media\c.png", "image")

        roots = [r"C:\Media"]

        page1 = list_media_in_scope(conn, roots, limit=2, offset=0)
        self.assertEqual([r["path"] for r in page1], ["c:/media/a.png", "c:/media/b.png"])

        page2 = list_media_in_scope(conn, roots, limit=2, offset=2)
        self.assertEqual([r["path"] for r in page2], ["c:/media/c.png"])

        page3 = list_media_in_scope(conn, roots, limit=2, offset=4)
        self.assertEqual(page3, [])


if __name__ == "__main__":
    unittest.main()
