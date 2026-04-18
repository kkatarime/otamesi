from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PIL import Image
import numpy as np


def pil_to_qpixmap(image: Image.Image) -> QPixmap:
    if image.mode == "RGBA":
        data = image.tobytes("raw", "RGBA")
        qimg = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
    else:
        rgb = image.convert("RGB")
        data = rgb.tobytes("raw", "RGB")
        qimg = QImage(data, image.width, image.height, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


class CanvasWidget(QGraphicsView):
    image_loaded = pyqtSignal(str)  # ファイルパスを通知

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)
        self.setScene(self._scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setStyleSheet("background: #2b2b2b; border: none;")

        self._image: Image.Image | None = None

    def load_image(self, image: Image.Image):
        self._image = image
        pixmap = pil_to_qpixmap(image)
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)

    def update_image(self, image: Image.Image):
        self._image = image
        pixmap = pil_to_qpixmap(image)
        self._pixmap_item.setPixmap(pixmap)

    @property
    def current_image(self) -> Image.Image | None:
        return self._image

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image:
            self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
