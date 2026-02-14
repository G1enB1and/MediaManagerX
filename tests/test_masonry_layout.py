import unittest

from app.mediamanager.layout.masonry import MasonryItem, layout_masonry


class TestMasonryLayout(unittest.TestCase):
    def test_basic_positions_shortest_column(self):
        # 2 columns, fixed widths
        items = [
            MasonryItem("a", aspect_ratio=1.0),  # h = w
            MasonryItem("b", aspect_ratio=1.0),
            MasonryItem("c", aspect_ratio=1.0),
        ]
        placements, total = layout_masonry(
            container_width_px=220, columns=2, gutter_px=20, items=items
        )
        # usable=200 => col_w=100
        self.assertEqual([p.width for p in placements], [100, 100, 100])

        # First item in col0 at y=0
        self.assertEqual((placements[0].column, placements[0].x, placements[0].y), (0, 0, 0))
        # Second item in col1 at y=0
        self.assertEqual((placements[1].column, placements[1].x, placements[1].y), (1, 120, 0))
        # Third item goes back to col0 (tie resolved to lowest index)
        self.assertEqual((placements[2].column, placements[2].x, placements[2].y), (0, 0, 120))

        # Total height: max(column heights) minus gutter
        self.assertEqual(total, 220)

    def test_fallback_height_when_aspect_unknown(self):
        items = [MasonryItem("x", aspect_ratio=None, fallback_height_px=333)]
        placements, total = layout_masonry(
            container_width_px=300, columns=3, gutter_px=0, items=items
        )
        self.assertEqual(placements[0].height, 333)
        self.assertEqual(total, 333)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            layout_masonry(container_width_px=0, columns=3, gutter_px=10, items=[])
        with self.assertRaises(ValueError):
            layout_masonry(container_width_px=100, columns=0, gutter_px=10, items=[])
        with self.assertRaises(ValueError):
            layout_masonry(container_width_px=10, columns=2, gutter_px=20, items=[])


if __name__ == "__main__":
    unittest.main()
