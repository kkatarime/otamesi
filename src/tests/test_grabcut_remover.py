import sys
import os
import unittest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ai.grabcut_remover import remove_background_by_rect


class TestRemoveBackgroundByRect(unittest.TestCase):
    def _make_image(self, w=200, h=200):
        return Image.new("RGB", (w, h), color=(100, 150, 200))

    def test_returns_rgba(self):
        img = self._make_image()
        result, elapsed = remove_background_by_rect(img, (10, 10, 80, 80))
        self.assertEqual(result.mode, "RGBA")

    def test_elapsed_is_non_negative(self):
        img = self._make_image()
        _, elapsed = remove_background_by_rect(img, (10, 10, 80, 80))
        self.assertGreaterEqual(elapsed, 0.0)

    def test_output_same_size(self):
        img = self._make_image(300, 250)
        result, _ = remove_background_by_rect(img, (20, 20, 100, 80))
        self.assertEqual(result.size, (300, 250))

    def test_rect_clamp_out_of_bounds(self):
        img = self._make_image(100, 100)
        # 範囲が画像をはみ出してもクラッシュしない
        result, _ = remove_background_by_rect(img, (80, 80, 100, 100))
        self.assertEqual(result.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
