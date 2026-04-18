from PyQt5.QtWidgets import QToolBar, QAction, QActionGroup
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class ToolbarWidget(QToolBar):
    open_requested = pyqtSignal()
    save_requested = pyqtSignal()
    mode_changed = pyqtSignal(str)  # "bg_remove" | "inpaint" | "upscale"

    def __init__(self, parent=None):
        super().__init__("メインツールバー", parent)
        self.setMovable(False)
        self._build()

    def _build(self):
        open_act = QAction("📂 開く", self)
        open_act.setStatusTip("画像ファイルを開く")
        open_act.triggered.connect(self.open_requested)
        self.addAction(open_act)

        save_act = QAction("💾 保存", self)
        save_act.setStatusTip("処理済み画像を保存")
        save_act.triggered.connect(self.save_requested)
        self.addAction(save_act)

        self.addSeparator()

        group = QActionGroup(self)
        group.setExclusive(True)

        modes = [
            ("🔲 背景除去", "bg_remove", "背景をワンクリックで透過PNGに変換"),
            ("✏️ 生成塗りつぶし", "inpaint", "マスクした領域をAIで埋める（要GPU推奨）"),
            ("🔍 高解像度化", "upscale", "画像を4倍拡大（Real-ESRGAN）"),
        ]
        for label, mode_id, tip in modes:
            act = QAction(label, self)
            act.setStatusTip(tip)
            act.setCheckable(True)
            act.setData(mode_id)
            act.triggered.connect(lambda checked, m=mode_id: self.mode_changed.emit(m))
            group.addAction(act)
            self.addAction(act)

        group.actions()[0].setChecked(True)
