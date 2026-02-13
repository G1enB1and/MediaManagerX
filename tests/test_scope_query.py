import unittest

from app.mediamanager.db.scope_query import build_scope_where_clause


class TestScopeQuery(unittest.TestCase):
    def test_empty_selection_returns_false_predicate(self) -> None:
        self.assertEqual(build_scope_where_clause([]), "0")

    def test_builds_equal_or_descendant_predicates(self) -> None:
        clause = build_scope_where_clause([r"C:\\Media\\Cats"])
        self.assertIn("path = 'c:/media/cats'", clause)
        self.assertIn("path LIKE 'c:/media/cats/%'", clause)

    def test_dedupes_and_normalizes(self) -> None:
        clause = build_scope_where_clause([
            r"C:\\Media\\Cats",
            r"c:/media/cats/",
        ])
        self.assertEqual(clause.count("path ="), 1)


if __name__ == "__main__":
    unittest.main()
