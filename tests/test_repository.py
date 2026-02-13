import sqlite3
import unittest
from pathlib import Path

from app.mediamanager.db.migrations import init_db
from app.mediamanager.db.repository import MediaRepository


class TestRepository(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        self.db_path = tmp_dir / 'repository.db'
        if self.db_path.exists():
            self.db_path.unlink()
        init_db(str(self.db_path))

    def test_end_to_end_foundation_flow(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            repo = MediaRepository(conn)
            media_id = repo.ingest_media(r"C:\\Media\\Cats\\a.jpg", 'image')

            repo.set_selection([r"C:\\Media\\Cats"])
            self.assertEqual(repo.current_selection(), ['c:/media/cats'])

            items = repo.scoped_media()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]['id'], media_id)

            repo.save_metadata(media_id, title='Cat Pic', notes='favorite')
            metadata = repo.load_metadata(media_id)
            self.assertIsNotNone(metadata)
            assert metadata is not None
            self.assertEqual(metadata['title'], 'Cat Pic')

            repo.add_tags(media_id, ['cat', 'cute'])
            self.assertEqual(repo.get_tags(media_id), ['cat', 'cute'])


if __name__ == '__main__':
    unittest.main()
