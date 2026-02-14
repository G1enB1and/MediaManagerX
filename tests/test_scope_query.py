import unittest

from app.mediamanager.db.scope_query import build_scope_where, build_scope_where_clause


class TestScopeQuery(unittest.TestCase):
    def test_empty_selection_returns_false_predicate(self) -> None:
        sql, params = build_scope_where([])
        self.assertEqual(sql, "0")
        self.assertEqual(params, [])

    def test_builds_equal_or_descendant_predicates(self) -> None:
        sql, params = build_scope_where([r"C:\\Media\\Cats"])
        self.assertIn("(path = ? OR path LIKE ?)", sql)
        self.assertEqual(params, ["c:/media/cats", "c:/media/cats/%"])

        # Back-compat debug view
        clause = build_scope_where_clause([r"C:\\Media\\Cats"])
        self.assertIn("path = 'c:/media/cats'", clause)
        self.assertIn("path LIKE 'c:/media/cats/%'", clause)

    def test_dedupes_and_normalizes(self) -> None:
        sql, params = build_scope_where([
            r"C:\\Media\\Cats",
            r"c:/media/cats/",
        ])
        self.assertEqual(sql.count("path = ?"), 1)
        self.assertEqual(params, ["c:/media/cats", "c:/media/cats/%"])


if __name__ == "__main__":
    unittest.main()
