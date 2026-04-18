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


if __name__ == "__main__":
    unittest.main()
