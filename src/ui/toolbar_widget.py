from PyQt5.QtWidgets import QToolBar, QAction, QActionGroup
from PyQt5.QtCore import pyqtSignal


class ToolbarWidget(QToolBar):
    open_requested = pyqtSignal()
    save_requested = pyqtSignal()
    run_requested = pyqtSignal(str)  # 実行ボタン → 現在のモードIDを送る

    def __init__(self, parent=None):
        super().__init__("メインツールバー", parent)
        self.setMovable(False)
        self._current_mode = "bg_remove"
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
            ("🔲 背景除去", "bg_remove", "AIが自動で背景を透過PNGに変換"),
            ("✂️ 選択除去", "select_remove", "矩形を描いて囲んだ範囲だけ残し背景を除去"),
            ("✏️ 生成塗りつぶし", "inpaint", "マスク領域をAIで埋める（要GPU推奨）"),
            ("🔍 高解像度化", "upscale", "画像を4倍拡大（Real-ESRGAN）"),
        ]
        for label, mode_id, tip in modes:
            act = QAction(label, self)
            act.setStatusTip(tip)
            act.setCheckable(True)
            act.setData(mode_id)
            act.triggered.connect(lambda checked, m=mode_id: self._on_mode_selected(m))
            group.addAction(act)
            self.addAction(act)

        group.actions()[0].setChecked(True)

        self.addSeparator()

        self._run_act = QAction("▶ 実行", self)
        self._run_act.setStatusTip("選択中の機能を実行")
        self._run_act.triggered.connect(
            lambda: self.run_requested.emit(self._current_mode)
        )
        self.addAction(self._run_act)

    def _on_mode_selected(self, mode_id: str):
        self._current_mode = mode_id
        labels = {
            "bg_remove": "▶ 背景除去を実行",
            "select_remove": "▶ 選択範囲で除去（矩形を描いてから実行）",
            "inpaint": "▶ 生成塗りつぶしを実行",
            "upscale": "▶ 高解像度化を実行",
        }
        self._run_act.setText(labels.get(mode_id, "▶ 実行"))
