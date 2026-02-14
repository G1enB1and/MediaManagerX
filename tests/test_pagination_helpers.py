import unittest

from app.mediamanager.db.pagination import page_to_limit_offset


class TestPaginationHelpers(unittest.TestCase):
    def test_page_to_limit_offset(self):
        self.assertEqual(page_to_limit_offset(page=1, page_size=100), (100, 0))
        self.assertEqual(page_to_limit_offset(page=2, page_size=100), (100, 100))
        self.assertEqual(page_to_limit_offset(page=3, page_size=25), (25, 50))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            page_to_limit_offset(page=0, page_size=10)
        with self.assertRaises(ValueError):
            page_to_limit_offset(page=1, page_size=0)


if __name__ == "__main__":
    unittest.main()
