import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image

from ui.canvas_widget import CanvasWidget
from ui.toolbar_widget import ToolbarWidget
from ui.progress_dialog import ProgressDialog


class _BgRemoveThread(QThread):
    finished  = pyqtSignal(object, float)   # (Image, elapsed)
    progress  = pyqtSignal(str)             # ステージメッセージ
    error     = pyqtSignal(str)

    def __init__(self, image: Image.Image):
        super().__init__()
        self._image    = image
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            from ai.background_remover import remove_background

            def cb(msg: str):
                if not self._cancelled:
                    self.progress.emit(msg)

            result, elapsed = remove_background(self._image, progress_cb=cb)

            if not self._cancelled:
                self.finished.emit(result, elapsed)

        except BaseException as exc:
            if not self._cancelled:
                self.error.emit(f"{type(exc).__name__}: {exc}")


class _SelectRemoveThread(QThread):
    finished = pyqtSignal(object, float)
    error    = pyqtSignal(str)

    def __init__(self, image: Image.Image, rect: tuple):
        super().__init__()
        self._image = image
        self._rect  = rect

    def run(self):
        try:
            from ai.grabcut_remover import remove_background_by_rect
            result, elapsed = remove_background_by_rect(self._image, self._rect)
            self.finished.emit(result, elapsed)
        except BaseException as exc:
            self.error.emit(f"{type(exc).__name__}: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ローカルAI画像エディタ")
        self.setMinimumSize(900, 620)
        self._current_mode   = "bg_remove"
        self._pending_rect: tuple | None = None
        self._worker: QThread | None = None
        self._build()

    def _build(self):
        self._toolbar = ToolbarWidget(self)
        self._toolbar.open_requested.connect(self._open_image)
        self._toolbar.save_requested.connect(self._save_image)
        self._toolbar.run_requested.connect(self._on_run)
        self.addToolBar(self._toolbar)

        self._canvas = CanvasWidget()
        self._canvas.rect_selected.connect(self._on_rect_selected)
        self.setCentralWidget(self._canvas)

        self._status = QLabel("画像を開いて「▶ 実行」を押してください")
        self.statusBar().addWidget(self._status)

    # ── ファイル操作 ──────────────────────────────────────

    def _open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "画像を開く", "",
            "画像ファイル (*.png *.jpg *.jpeg *.webp *.bmp *.tiff)",
        )
        if not path:
            return
        self._canvas.load_image(Image.open(path))
        self._pending_rect = None
        self._status.setText(os.path.basename(path))

    def _save_image(self):
        image = self._canvas.current_image
        if image is None:
            QMessageBox.information(self, "保存", "保存する画像がありません。")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "名前を付けて保存", "", "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if path:
            image.save(path)
            self._status.setText(f"保存完了: {os.path.basename(path)}")

    # ── モード切替・実行 ──────────────────────────────────

    def _on_run(self, mode: str):
        self._current_mode = mode
        self._canvas.set_select_mode(mode == "select_remove")
        {
            "bg_remove":     self._run_bg_remove,
            "select_remove": self._run_select_remove,
            "inpaint":  lambda: QMessageBox.information(self, "生成塗りつぶし", "Sprint 3で実装予定です。"),
            "upscale":  lambda: QMessageBox.information(self, "高解像度化", "Sprint 3で実装予定です。"),
        }.get(mode, lambda: None)()

    # ── 自動背景除去 ──────────────────────────────────────

    def _run_bg_remove(self):
        image = self._canvas.current_image
        if image is None:
            QMessageBox.information(self, "背景除去", "先に画像を開いてください。")
            return

        from ai.background_remover import is_model_cached
        if not is_model_cached():
            if QMessageBox.question(
                self, "初回モデルダウンロード",
                "AIモデル（約167MB）が必要です。\n"
                "コマンドラインで以下を実行してください:\n\n"
                "  python -c \"from rembg import remove\"\n\n"
                "（初回のみ。完了後に再度「▶ 背景除去を実行」してください）",
                QMessageBox.Ok,
            ):
                return

        est = "数秒" if max(image.size) <= 1500 else "30秒〜数分（大きな画像）"
        dlg = ProgressDialog(
            f"背景を除去しています…\n"
            f"サイズ: {image.width}×{image.height}px  目安: {est}",
            self,
            cancelable=True,
        )
        worker = _BgRemoveThread(image)
        self._worker = worker

        worker.progress.connect(dlg.set_message)
        worker.finished.connect(lambda img, t: self._on_done(img, t, dlg, "背景除去"))
        worker.error.connect(lambda e: self._on_error(e, dlg))
        dlg.cancel_requested.connect(worker.cancel)

        worker.start()
        dlg.exec_()

    # ── 選択範囲除去 ──────────────────────────────────────

    def _on_rect_selected(self, x: int, y: int, w: int, h: int):
        self._pending_rect = (x, y, w, h)
        self._status.setText(
            f"選択範囲: ({x}, {y})  {w}×{h}px — 「▶ 実行」で矩形外を透明化"
        )

    def _run_select_remove(self):
        image = self._canvas.current_image
        if image is None:
            QMessageBox.information(self, "選択除去", "先に画像を開いてください。")
            return
        if not self._pending_rect:
            self._status.setText("✂️ 選択除去: 画像上でドラッグして範囲を選んでから「▶ 実行」")
            return

        dlg = ProgressDialog("矩形外を透明化しています…", self)
        worker = _SelectRemoveThread(image, self._pending_rect)
        self._worker = worker
        worker.finished.connect(lambda img, t: self._on_done(img, t, dlg, "選択除去"))
        worker.error.connect(lambda e: self._on_error(e, dlg))
        worker.start()
        dlg.exec_()

    # ── 共通完了・エラー ──────────────────────────────────

    def _on_done(self, image: Image.Image, elapsed: float, dlg: ProgressDialog, label: str):
        if dlg.cancelled:
            return
        dlg.accept()
        self._canvas.update_image(image)
        self._canvas.set_select_mode(False)
        self._pending_rect = None
        self._status.setText(f"{label}完了 ({elapsed:.1f}秒) — 💾 保存で書き出せます")

    def _on_error(self, message: str, dlg: ProgressDialog):
        if dlg.cancelled:
            return
        dlg.reject()
        QMessageBox.critical(self, "処理エラー", message)
