import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QFileDialog, QPushButton, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor

SUPPORTED_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
}

ICON_MAP = {
    "video": "🎬",
    "audio": "🎵",
}

VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"}


class FileBrowser(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_folder = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QHBoxLayout()
        self._folder_label = QLabel("フォルダ未選択")
        self._folder_label.setWordWrap(True)
        open_btn = QPushButton("📂 開く")
        open_btn.setFixedWidth(64)
        open_btn.clicked.connect(self.open_folder)
        header.addWidget(self._folder_label, 1)
        header.addWidget(open_btn)
        layout.addLayout(header)

        self._count_label = QLabel("")
        layout.addWidget(self._count_label)

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        self._list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self._list)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "メディアフォルダを選択", self._current_folder or ""
        )
        if folder:
            self._current_folder = folder
            self._load_folder(folder)

    def _load_folder(self, folder: str):
        self._list.clear()
        entries = []
        for name in sorted(os.listdir(folder)):
            ext = os.path.splitext(name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                entries.append((name, ext))

        for name, ext in entries:
            icon = ICON_MAP["video"] if ext in VIDEO_EXTS else ICON_MAP["audio"]
            full_path = os.path.join(folder, name)
            size_kb = os.path.getsize(full_path) // 1024
            item = QListWidgetItem(f"{icon}  {name}  ({size_kb} KB)")
            item.setData(Qt.UserRole, full_path)
            self._list.addItem(item)

        short = os.path.basename(folder)
        self._folder_label.setText(short)
        self._count_label.setText(f"{len(entries)} ファイル")

    def _on_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path:
            self.file_selected.emit(path)
