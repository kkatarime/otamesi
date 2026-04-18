import sys
import os
import unittest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt5.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from ui.canvas_widget import pil_to_qpixmap, CanvasWidget


class TestPilToQPixmap(unittest.TestCase):
    def test_rgb_image(self):
        img = Image.new("RGB", (100, 80), color=(255, 0, 0))
        pix = pil_to_qpixmap(img)
        self.assertEqual(pix.width(), 100)
        self.assertEqual(pix.height(), 80)

    def test_rgba_image(self):
        img = Image.new("RGBA", (50, 60), color=(0, 255, 0, 128))
        pix = pil_to_qpixmap(img)
        self.assertEqual(pix.width(), 50)
        self.assertEqual(pix.height(), 60)


class TestCanvasWidget(unittest.TestCase):
    def setUp(self):
        self.canvas = CanvasWidget()

    def test_initial_no_image(self):
        self.assertIsNone(self.canvas.current_image)

    def test_load_image(self):
        img = Image.new("RGB", (200, 150))
        self.canvas.load_image(img)
        self.assertIsNotNone(self.canvas.current_image)
        self.assertEqual(self.canvas.current_image.size, (200, 150))

    def test_update_image(self):
        img1 = Image.new("RGB", (100, 100), "red")
        img2 = Image.new("RGBA", (200, 200), "blue")
        self.canvas.load_image(img1)
        self.canvas.update_image(img2)
        self.assertEqual(self.canvas.current_image.mode, "RGBA")


class TestBrushMode(unittest.TestCase):
    def setUp(self):
        self.canvas = CanvasWidget()
        self.canvas.load_image(Image.new("RGB", (200, 200), "white"))

    def test_get_mask_initially_empty(self):
        mask = self.canvas.get_mask()
        import numpy as np
        self.assertFalse(np.any(np.array(mask) > 0))

    def test_brush_draws_on_mask(self):
        from PyQt5.QtCore import QPointF
        self.canvas.set_brush_mode(True)
        self.canvas.set_brush_radius(10)
        self.canvas._draw_brush(QPointF(100, 100), erase=False)
        import numpy as np
        mask = self.canvas.get_mask()
        self.assertTrue(np.any(np.array(mask) > 0))

    def test_brush_erase_clears_mask(self):
        from PyQt5.QtCore import QPointF
        self.canvas.set_brush_mode(True)
        self.canvas.set_brush_radius(10)
        self.canvas._draw_brush(QPointF(100, 100), erase=False)
        self.canvas._draw_brush(QPointF(100, 100), erase=True)
        import numpy as np
        mask_arr = np.array(self.canvas.get_mask())
        self.assertFalse(np.any(mask_arr[90:111, 90:111] > 0))

    def test_set_brush_mode_off_restores_cursor(self):
        self.canvas.set_brush_mode(True)
        self.assertTrue(self.canvas._brush_mode)
        self.canvas.set_brush_mode(False)
        self.assertFalse(self.canvas._brush_mode)

    def test_load_image_resets_mask(self):
        from PyQt5.QtCore import QPointF
        self.canvas.set_brush_mode(True)
        self.canvas._draw_brush(QPointF(100, 100), erase=False)
        self.canvas.load_image(Image.new("RGB", (100, 100), "red"))
        import numpy as np
        mask = self.canvas.get_mask()
        self.assertFalse(np.any(np.array(mask) > 0))


if __name__ == "__main__":
    unittest.main()
