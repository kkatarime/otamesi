from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QToolBar, QAction, QLabel
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from ui.file_browser import FileBrowser
from ui.media_player_widget import MediaPlayerWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("メディアマネージャー")
        self.setMinimumSize(1000, 650)
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()

    def _build_toolbar(self):
        toolbar = QToolBar("メインツールバー")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_action = QAction("📂 フォルダを開く", self)
        open_action.setStatusTip("メディアフォルダを選択します")
        open_action.triggered.connect(self._on_open_folder)
        toolbar.addAction(open_action)

    def _build_central(self):
        splitter = QSplitter(Qt.Horizontal)

        self.file_browser = FileBrowser()
        self.file_browser.setMinimumWidth(280)
        self.file_browser.file_selected.connect(self._on_file_selected)

        self.player_widget = MediaPlayerWidget()

        splitter.addWidget(self.file_browser)
        splitter.addWidget(self.player_widget)
        splitter.setSizes([300, 700])
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

    def _build_statusbar(self):
        self.status_label = QLabel("フォルダを選択してください")
        self.statusBar().addWidget(self.status_label)

    def _on_open_folder(self):
        self.file_browser.open_folder()

    def _on_file_selected(self, file_path: str):
        self.player_widget.load(file_path)
        self.status_label.setText(file_path)
