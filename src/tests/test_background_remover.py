import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestRemoveBackground(unittest.TestCase):
    def test_returns_rgba_and_elapsed(self):
        rgba_result = Image.new("RGBA", (100, 100))
        mock_rembg = MagicMock()
        mock_rembg.remove.return_value = rgba_result
        with patch.dict("sys.modules", {"rembg": mock_rembg}):
            import ai.background_remover as bg_mod
            import importlib
            importlib.reload(bg_mod)
            result, elapsed = bg_mod.remove_background(Image.new("RGB", (100, 100)))
        self.assertEqual(result.mode, "RGBA")
        self.assertGreaterEqual(elapsed, 0.0)

    def test_elapsed_is_float(self):
        rgba_result = Image.new("RGBA", (50, 50))
        mock_rembg = MagicMock()
        mock_rembg.remove.return_value = rgba_result
        with patch.dict("sys.modules", {"rembg": mock_rembg}):
            import ai.background_remover as bg_mod
            import importlib
            importlib.reload(bg_mod)
            _, elapsed = bg_mod.remove_background(Image.new("RGB", (50, 50)))
        self.assertIsInstance(elapsed, float)


if __name__ == "__main__":
    unittest.main()
