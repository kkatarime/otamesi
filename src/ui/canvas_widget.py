from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QBrush
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
    rect_selected = pyqtSignal(int, int, int, int)  # x, y, w, h（画像ピクセル座標）

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
        self.setStyleSheet("background: #071018; border: none;")

        self._image: Image.Image | None = None
        self._select_mode = False
        self._brush_mode = False
        self._brush_erase = False
        self._brush_radius = 20
        self._drag_start: QPointF | None = None
        self._sel_rect_item: QGraphicsRectItem | None = None

        # マスクオーバーレイ用（ブラシモード）
        self._mask_arr: np.ndarray | None = None
        self._mask_pixmap_item: QGraphicsPixmapItem | None = None
        self._overlay_data: bytes | None = None  # QImageのGC防止

    # ── 公開API ──────────────────────────────────────────

    def load_image(self, image: Image.Image):
        self._image = image
        pixmap = pil_to_qpixmap(image)
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
        self._clear_selection()
        self._reset_mask()

    def update_image(self, image: Image.Image):
        self._image = image
        pixmap = pil_to_qpixmap(image)
        self._pixmap_item.setPixmap(pixmap)
        self._clear_selection()
        self._reset_mask()

    def set_select_mode(self, enabled: bool):
        self._select_mode = enabled
        self._brush_mode = False
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._clear_selection()

    def set_brush_mode(self, enabled: bool, erase: bool = False):
        self._brush_mode = enabled
        self._brush_erase = erase
        self._select_mode = False
        if enabled:
            self.setCursor(Qt.CrossCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            if self._image and self._mask_arr is None:
                self._reset_mask()
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_brush_radius(self, radius: int):
        self._brush_radius = max(1, radius)

    def clear_mask(self):
        self._reset_mask()

    def get_mask(self) -> "Image.Image | None":
        """ブラシで描いたマスクを PIL Image(L mode) で返す。白=塗りつぶし対象"""
        if self._mask_arr is None:
            return None
        return Image.fromarray(self._mask_arr, "L")

    @property
    def current_image(self) -> "Image.Image | None":
        return self._image

    # ── マスク管理 ────────────────────────────────────────

    def _reset_mask(self):
        if self._mask_pixmap_item:
            self._scene.removeItem(self._mask_pixmap_item)
            self._mask_pixmap_item = None
        if self._image:
            self._mask_arr = np.zeros(
                (self._image.height, self._image.width), dtype=np.uint8
            )
        else:
            self._mask_arr = None

    def _update_mask_overlay(self):
        if self._mask_arr is None or self._image is None:
            return
        h, w = self._mask_arr.shape
        overlay = np.zeros((h, w, 4), dtype=np.uint8)
        overlay[self._mask_arr > 0] = [255, 80, 80, 160]  # 赤半透明
        # bytesPerLine を明示して QImage が正しくデータを読む
        bytes_per_line = w * 4
        self._overlay_data = overlay.tobytes()  # GC防止のためインスタンス変数で保持
        qimg = QImage(self._overlay_data, w, h, bytes_per_line, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        if self._mask_pixmap_item is None:
            self._mask_pixmap_item = self._scene.addPixmap(pix)
            self._mask_pixmap_item.setZValue(1)
        else:
            self._mask_pixmap_item.setPixmap(pix)

    def _draw_brush(self, scene_pt: QPointF, erase: bool):
        if self._mask_arr is None or self._image is None:
            return
        cx, cy = int(scene_pt.x()), int(scene_pt.y())
        r = self._brush_radius
        h, w = self._mask_arr.shape
        y0, y1 = max(0, cy - r), min(h, cy + r + 1)
        x0, x1 = max(0, cx - r), min(w, cx + r + 1)
        ys, xs = np.ogrid[y0:y1, x0:x1]
        circle = (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r
        self._mask_arr[y0:y1, x0:x1][circle] = 0 if erase else 255
        self._update_mask_overlay()

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

    # ── マウスイベント ────────────────────────────────────

    def mousePressEvent(self, event):
        pt = self._scene_point(event)
        if self._brush_mode and event.button() == Qt.LeftButton and self._image:
            self._draw_brush(pt, erase=self._brush_erase)
            return
        if self._brush_mode and event.button() == Qt.RightButton and self._image:
            self._draw_brush(pt, erase=True)
            return
        if self._select_mode and event.button() == Qt.LeftButton and self._image:
            self._clear_selection()
            self._drag_start = self._clamp_to_image(pt)
            pen = QPen(QColor(0, 200, 255), 1.5, Qt.DashLine)
            self._sel_rect_item = self._scene.addRect(
                QRectF(self._drag_start, self._drag_start), pen
            )
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pt = self._scene_point(event)
        if self._brush_mode and event.buttons() & (Qt.LeftButton | Qt.RightButton) and self._image:
            erase = bool(event.buttons() & Qt.RightButton) or self._brush_erase
            self._draw_brush(pt, erase=erase)
            return
        if self._select_mode and self._drag_start and self._sel_rect_item:
            cur = self._clamp_to_image(pt)
            self._sel_rect_item.setRect(QRectF(self._drag_start, cur).normalized())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._brush_mode:
            return
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
