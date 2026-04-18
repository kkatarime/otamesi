from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea,
    QWidget, QLabel, QGridLayout, QPushButton, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PIL import Image

GALLERY_DIR = Path.home() / "Pictures" / "ローカルAI画像エディタ"


def ensure_gallery_dir():
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)


def save_to_gallery(image: Image.Image, label: str) -> Path:
    ensure_gallery_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = GALLERY_DIR / f"{label}_{ts}.png"
    image.save(str(path))
    return path


def _pil_to_qpixmap_thumb(image: Image.Image, size: int = 160) -> QPixmap:
    thumb = image.copy()
    thumb.thumbnail((size, size), Image.LANCZOS)
    if thumb.mode != "RGBA":
        thumb = thumb.convert("RGBA")
    data = thumb.tobytes("raw", "RGBA")
    from PyQt5.QtGui import QImage
    qimg = QImage(data, thumb.width, thumb.height,
                  thumb.width * 4, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg.copy())


class _ThumbCard(QWidget):
    clicked = pyqtSignal(Path)

    def __init__(self, path: Path, parent=None):
        super().__init__(parent)
        self._path = path
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        try:
            with Image.open(path) as img:
                pix = _pil_to_qpixmap_thumb(img.copy())
        except Exception:
            pix = QPixmap(160, 160)
            pix.fill(Qt.gray)

        img_label = QLabel()
        img_label.setPixmap(pix)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setFixedSize(164, 164)
        img_label.setStyleSheet("border: 1px solid #1e3a5a; background: #071018;")
        layout.addWidget(img_label)

        name_label = QLabel(path.stem[:20])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #7aa0c0; font-size: 10px;")
        layout.addWidget(name_label)

        self.setFixedWidth(172)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QWidget:hover { background: #0f2030; border-radius: 4px; }")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._path)


class GalleryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ギャラリー")
        self.setMinimumSize(700, 500)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel(f"📁 {GALLERY_DIR}")
        title.setStyleSheet("color: #7aa0c0; font-size: 11px;")
        header.addWidget(title)
        header.addStretch()
        open_btn = QPushButton("フォルダを開く")
        open_btn.clicked.connect(self._open_folder)
        header.addWidget(open_btn)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        container = QWidget()
        self._grid = QGridLayout(container)
        self._grid.setSpacing(8)
        self._grid.setContentsMargins(8, 8, 8, 8)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        self._preview_label = QLabel("サムネイルをクリックでプレビュー")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setFixedHeight(48)
        self._preview_label.setStyleSheet("color: #7aa0c0; font-size: 11px;")
        layout.addWidget(self._preview_label)

        self._load_images()

    def _load_images(self):
        ensure_gallery_dir()
        files = sorted(GALLERY_DIR.glob("*.png"), reverse=True)

        if not files:
            empty = QLabel("まだ画像がありません")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #7aa0c0; font-size: 14px;")
            self._grid.addWidget(empty, 0, 0)
            return

        cols = 4
        for i, path in enumerate(files):
            card = _ThumbCard(path)
            card.clicked.connect(self._on_thumb_clicked)
            self._grid.addWidget(card, i // cols, i % cols)

    def _on_thumb_clicked(self, path: Path):
        self._preview_label.setText(f"✅ {path.name}")
        import subprocess, os
        try:
            os.startfile(str(path))
        except Exception:
            pass

    def _open_folder(self):
        import subprocess
        ensure_gallery_dir()
        subprocess.Popen(f'explorer "{GALLERY_DIR}"')
