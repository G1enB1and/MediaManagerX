import unittest

from app.mediamanager.layout.columns import choose_columns


class TestChooseColumns(unittest.TestCase):
    def test_minimum_one_column(self):
        self.assertEqual(
            choose_columns(
                container_width_px=100,
                min_column_width_px=500,
                gutter_px=10,
                max_columns=12,
            ),
            1,
        )

    def test_accounts_for_gutter(self):
        # container 320, min 150, gutter 10
        # N <= (320+10)/(150+10)=330/160=2
        self.assertEqual(
            choose_columns(
                container_width_px=320,
                min_column_width_px=150,
                gutter_px=10,
            ),
            2,
        )

    def test_clamped_to_max(self):
        self.assertEqual(
            choose_columns(
                container_width_px=10000,
                min_column_width_px=10,
                gutter_px=0,
                max_columns=3,
            ),
            3,
        )

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            choose_columns(container_width_px=0, min_column_width_px=100, gutter_px=0)
        with self.assertRaises(ValueError):
            choose_columns(container_width_px=100, min_column_width_px=0, gutter_px=0)
        with self.assertRaises(ValueError):
            choose_columns(container_width_px=100, min_column_width_px=100, gutter_px=-1)
        with self.assertRaises(ValueError):
            choose_columns(container_width_px=100, min_column_width_px=100, gutter_px=0, max_columns=0)


if __name__ == "__main__":
    unittest.main()
