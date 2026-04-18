import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt5.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)

from ui.file_browser import FileBrowser, SUPPORTED_EXTENSIONS, VIDEO_EXTS, AUDIO_EXTS


class TestFileBrowserConstants(unittest.TestCase):
    def test_supported_extensions_not_empty(self):
        self.assertTrue(len(SUPPORTED_EXTENSIONS) > 0)

    def test_video_audio_disjoint(self):
        self.assertEqual(VIDEO_EXTS & AUDIO_EXTS, set())

    def test_all_video_audio_in_supported(self):
        self.assertTrue(VIDEO_EXTS.issubset(SUPPORTED_EXTENSIONS))
        self.assertTrue(AUDIO_EXTS.issubset(SUPPORTED_EXTENSIONS))


class TestFileBrowserUI(unittest.TestCase):
    def setUp(self):
        self.widget = FileBrowser()

    def test_initial_state(self):
        self.assertEqual(self.widget._count_label.text(), "")
        self.assertEqual(self.widget._list.count(), 0)

    def test_load_folder_filters_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "video.mp4"), "w").close()
            open(os.path.join(tmpdir, "audio.mp3"), "w").close()
            open(os.path.join(tmpdir, "doc.txt"), "w").close()
            self.widget._load_folder(tmpdir)
            self.assertEqual(self.widget._list.count(), 2)

    def test_file_selected_signal(self):
        received = []
        self.widget.file_selected.connect(received.append)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.mp3")
            open(path, "w").close()
            self.widget._load_folder(tmpdir)
            self.widget._list.setCurrentRow(0)
            self.widget._on_double_click(self.widget._list.item(0))
        self.assertEqual(len(received), 1)
        self.assertTrue(received[0].endswith("test.mp3"))


if __name__ == "__main__":
    unittest.main()
