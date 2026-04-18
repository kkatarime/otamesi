from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
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
    image_loaded = pyqtSignal(str)
    # 選択矩形が確定したとき (x, y, w, h) を画像ピクセル座標で通知
    rect_selected = pyqtSignal(int, int, int, int)

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
        self.setStyleSheet("background: #2b2b2b; border: none;")

        self._image: Image.Image | None = None
        self._select_mode = False
        self._drag_start: QPointF | None = None
        self._sel_rect_item: QGraphicsRectItem | None = None

    # ── 公開API ──────────────────────────────────────────

    def load_image(self, image: Image.Image):
        self._image = image
        pixmap = pil_to_qpixmap(image)
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
        self._clear_selection()

    def update_image(self, image: Image.Image):
        self._image = image
        pixmap = pil_to_qpixmap(image)
        self._pixmap_item.setPixmap(pixmap)
        self._clear_selection()

    def set_select_mode(self, enabled: bool):
        self._select_mode = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._clear_selection()

    @property
    def current_image(self) -> Image.Image | None:
        return self._image

    # ── 選択矩形 ─────────────────────────────────────────

    def _clear_selection(self):
        if self._sel_rect_item:
            self._scene.removeItem(self._sel_rect_item)
            self._sel_rect_item = None
        self._drag_start = None

    def _scene_point(self, event) -> QPointF:
        return self.mapToScene(event.pos())

    def _clamp_to_image(self, pt: QPointF) -> QPointF:
        if not self._image:
            return pt
        w, h = self._image.width, self._image.height
        return QPointF(max(0, min(pt.x(), w)), max(0, min(pt.y(), h)))

    def mousePressEvent(self, event):
        if self._select_mode and event.button() == Qt.LeftButton and self._image:
            self._clear_selection()
            self._drag_start = self._clamp_to_image(self._scene_point(event))
            pen = QPen(QColor(0, 200, 255), 1.5, Qt.DashLine)
            self._sel_rect_item = self._scene.addRect(
                QRectF(self._drag_start, self._drag_start), pen
            )
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._select_mode and self._drag_start and self._sel_rect_item:
            cur = self._clamp_to_image(self._scene_point(event))
            self._sel_rect_item.setRect(QRectF(self._drag_start, cur).normalized())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._select_mode and self._drag_start and event.button() == Qt.LeftButton:
            cur = self._clamp_to_image(self._scene_point(event))
            rect = QRectF(self._drag_start, cur).normalized()
            self._drag_start = None
            if rect.width() > 5 and rect.height() > 5:
                self.rect_selected.emit(
                    int(rect.x()), int(rect.y()),
                    int(rect.width()), int(rect.height())
                )
            return
        super().mouseReleaseEvent(event)

    # ── ズーム・リサイズ ──────────────────────────────────

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image:
            self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
