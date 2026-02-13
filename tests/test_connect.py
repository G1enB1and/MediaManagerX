import unittest
from pathlib import Path

from app.mediamanager.db.connect import connect_db


class TestConnect(unittest.TestCase):
    def test_connect_db_creates_blank_database_if_missing(self) -> None:
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        db_path = tmp_dir / 'connect-created.db'
        if db_path.exists():
            db_path.unlink()

        conn = connect_db(str(db_path))
        conn.close()

        self.assertTrue(db_path.exists())


if __name__ == '__main__':
    unittest.main()
