import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestRemoveBackground(unittest.TestCase):
    def test_returns_rgba_and_elapsed(self):
        rgba_result = Image.new("RGBA", (100, 100))

        with patch.dict("sys.modules", {"rembg": MagicMock(remove=lambda img: rgba_result)}):
            from ai import background_remover
            import importlib
            importlib.reload(background_remover)
            result, elapsed = background_remover.remove_background(Image.new("RGB", (100, 100)))

        self.assertEqual(result.mode, "RGBA")
        self.assertGreaterEqual(elapsed, 0.0)

    def test_elapsed_is_float(self):
        rgba_result = Image.new("RGBA", (50, 50))
        with patch.dict("sys.modules", {"rembg": MagicMock(remove=lambda img: rgba_result)}):
            from ai import background_remover
            import importlib
            importlib.reload(background_remover)
            _, elapsed = background_remover.remove_background(Image.new("RGB", (50, 50)))
        self.assertIsInstance(elapsed, float)


if __name__ == "__main__":
    unittest.main()
