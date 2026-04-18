import sys
import os
import unittest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ai.background_remover import is_model_cached, remove_background


class TestIsModelCached(unittest.TestCase):
    def test_returns_bool(self):
        self.assertIsInstance(is_model_cached(), bool)


@unittest.skipUnless(is_model_cached(), "モデル未ダウンロードのためスキップ")
class TestRemoveBackground(unittest.TestCase):
    def _img(self, w=80, h=80):
        return Image.new("RGB", (w, h), color=(120, 80, 200))

    def test_returns_rgba(self):
        result, _ = remove_background(self._img())
        self.assertEqual(result.mode, "RGBA")

    def test_same_size(self):
        img = self._img(150, 100)
        result, _ = remove_background(img)
        self.assertEqual(result.size, img.size)

    def test_elapsed_non_negative(self):
        _, elapsed = remove_background(self._img())
        self.assertGreaterEqual(elapsed, 0.0)

    def test_progress_callback_called(self):
        stages = []
        remove_background(self._img(), progress_cb=stages.append)
        self.assertGreater(len(stages), 0)

    def test_large_image_auto_resize(self):
        # 2000px画像でも正しいサイズで返る
        img = self._img(2000, 1500)
        result, _ = remove_background(img)
        self.assertEqual(result.size, (2000, 1500))


if __name__ == "__main__":
    unittest.main()
