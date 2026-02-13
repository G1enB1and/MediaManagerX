import unittest

from app.mediamanager.utils.pathing import is_under_root, normalize_windows_path


class TestPathing(unittest.TestCase):
    def test_normalize_windows_path_casefold_and_slashes(self) -> None:
        self.assertEqual(
            normalize_windows_path(r"C:\\Users\\Glen\\Pics\\A.JPG"),
            "c:/users/glen/pics/a.jpg",
        )

    def test_is_under_root_true_for_descendant_and_root(self) -> None:
        root = r"C:\\Users\\Glen\\Pics"
        self.assertTrue(is_under_root(r"C:\\Users\\Glen\\Pics\\cats\\x.png", root))
        self.assertTrue(is_under_root(r"C:\\Users\\Glen\\Pics", root))

    def test_is_under_root_false_for_sibling(self) -> None:
        root = r"C:\\Users\\Glen\\Pics"
        self.assertFalse(is_under_root(r"C:\\Users\\Glen\\Pictures\\x.png", root))


if __name__ == "__main__":
    unittest.main()
