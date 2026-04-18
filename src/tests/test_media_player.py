import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt5.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)

from ui.media_player_widget import _format_ms, MediaPlayerWidget


class TestFormatMs(unittest.TestCase):
    def test_seconds_only(self):
        self.assertEqual(_format_ms(5000), "0:05")

    def test_minutes_and_seconds(self):
        self.assertEqual(_format_ms(90000), "1:30")

    def test_hours(self):
        self.assertEqual(_format_ms(3661000), "1:01:01")

    def test_zero(self):
        self.assertEqual(_format_ms(0), "0:00")


class TestMediaPlayerWidget(unittest.TestCase):
    def setUp(self):
        self.widget = MediaPlayerWidget()

    def test_initial_volume(self):
        self.assertEqual(self.widget._player.volume(), 70)

    def test_initial_title(self):
        self.assertIn("選択", self.widget._title_label.text())

    def test_seek_slider_initial(self):
        self.assertEqual(self.widget._seek_slider.value(), 0)
        self.assertEqual(self.widget._seek_slider.maximum(), 0)


if __name__ == "__main__":
    unittest.main()
