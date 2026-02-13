import unittest
from pathlib import Path

from app.mediamanager.main import bootstrap_repository


class TestMainBootstrap(unittest.TestCase):
    def test_bootstrap_repository_creates_db(self) -> None:
        tmp_dir = Path('.tmp-tests')
        tmp_dir.mkdir(exist_ok=True)
        db_path = tmp_dir / 'main-bootstrap.db'
        if db_path.exists():
            db_path.unlink()

        repo = bootstrap_repository(str(db_path))
        self.assertIsNotNone(repo)
        self.assertTrue(db_path.exists())

    def test_bootstrap_repository_supports_nested_custom_path(self) -> None:
        tmp_dir = Path('.tmp-tests')
        db_path = tmp_dir / 'nested' / 'custom.db'
        if db_path.exists():
            db_path.unlink()

        repo = bootstrap_repository(str(db_path))
        self.assertIsNotNone(repo)
        self.assertTrue(db_path.exists())


if __name__ == '__main__':
    unittest.main()
