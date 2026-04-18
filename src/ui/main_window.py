import os
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QLabel, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image

from ui.canvas_widget import CanvasWidget
from ui.toolbar_widget import ToolbarWidget
from ui.progress_dialog import ProgressDialog


class _BgRemoveThread(QThread):
    finished = pyqtSignal(object, float)  # (Image, elapsed)
    error = pyqtSignal(str)

    def __init__(self, image: Image.Image):
        super().__init__()
        self._image = image

    def run(self):
        try:
            from ai.background_remover import remove_background
            result, elapsed = remove_background(self._image)
            self.finished.emit(result, elapsed)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ローカルAI画像エディタ")
        self.setMinimumSize(900, 620)
        self._current_mode = "bg_remove"
        self._worker: QThread | None = None
        self._build()

    def _build(self):
        self._toolbar = ToolbarWidget(self)
        self._toolbar.open_requested.connect(self._open_image)
        self._toolbar.save_requested.connect(self._save_image)
        self._toolbar.run_requested.connect(self._on_run)
        self.addToolBar(self._toolbar)

        self._canvas = CanvasWidget()
        self.setCentralWidget(self._canvas)

        self._status = QLabel("画像を開いて「▶ 実行」を押してください")
        self.statusBar().addWidget(self._status)

    def _open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "画像を開く", "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp *.bmp *.tiff)"
        )
        if not path:
            return
        image = Image.open(path)
        self._canvas.load_image(image)
        self._status.setText(os.path.basename(path))

    def _save_image(self):
        image = self._canvas.current_image
        if image is None:
            QMessageBox.information(self, "保存", "保存する画像がありません。")
            return
        default_ext = "*.png" if image.mode == "RGBA" else "*.jpg"
        path, _ = QFileDialog.getSaveFileName(
            self, "名前を付けて保存", "",
            f"PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if path:
            image.save(path)
            self._status.setText(f"保存完了: {os.path.basename(path)}")

    def _on_run(self, mode: str):
        self._current_mode = mode
        dispatch = {
            "bg_remove": self._run_bg_remove,
            "inpaint": lambda: QMessageBox.information(self, "生成塗りつぶし", "Sprint 3で実装予定です。"),
            "upscale": lambda: QMessageBox.information(self, "高解像度化", "Sprint 3で実装予定です。"),
        }
        dispatch.get(mode, lambda: None)()

    def _run_bg_remove(self):
        image = self._canvas.current_image
        if image is None:
            QMessageBox.information(self, "背景除去", "先に画像を開いてください。")
            return

        from ai.background_remover import is_model_cached
        if not is_model_cached():
            ret = QMessageBox.question(
                self, "初回モデルダウンロード",
                "AIモデル（約176MB）をダウンロードします。\n"
                "インターネット接続が必要です。続行しますか？",
            )
            if ret != QMessageBox.Yes:
                return

        msg = "背景を除去しています…"
        dlg = ProgressDialog(msg, self)
        self._worker = _BgRemoveThread(image)
        self._worker.finished.connect(lambda img, t: self._on_bg_done(img, t, dlg))
        self._worker.error.connect(lambda e: self._on_error(e, dlg))
        self._worker.start()
        dlg.exec_()

    def _on_bg_done(self, image: Image.Image, elapsed: float, dlg: ProgressDialog):
        dlg.accept()
        self._canvas.update_image(image)
        self._status.setText(f"背景除去完了 ({elapsed:.1f}秒) — 💾 保存で透過PNGに書き出せます")

    def _on_error(self, message: str, dlg: ProgressDialog):
        dlg.reject()
        QMessageBox.critical(self, "エラー", f"処理に失敗しました:\n{message}")
