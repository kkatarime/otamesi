from PyQt5.QtWidgets import QToolBar, QAction, QActionGroup, QPushButton, QWidget, QSizePolicy
from PyQt5.QtCore import pyqtSignal


class ToolbarWidget(QToolBar):
    open_requested    = pyqtSignal()
    save_requested    = pyqtSignal()
    run_requested     = pyqtSignal(str)
    mode_changed      = pyqtSignal(str)
    gallery_requested = pyqtSignal()

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

        gallery_act = QAction("🖼 ギャラリー", self)
        gallery_act.setStatusTip("保存済み画像一覧を表示")
        gallery_act.triggered.connect(self.gallery_requested)
        self.addAction(gallery_act)

        self.addSeparator()

        group = QActionGroup(self)
        group.setExclusive(True)

        modes = [
            ("🔲 背景除去",     "bg_remove",     "AIが自動で背景を透過PNGに変換"),
            ("✂️ 選択除去",     "select_remove", "矩形を描いて囲んだ範囲だけ残し背景を除去"),
            ("✏️ 生成塗りつぶし", "inpaint",       "マスク領域をAIで埋める"),
            ("🔍 高解像度化",   "upscale",       "画像を4倍拡大（Real-ESRGAN）"),
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

        # 実行ボタンは QPushButton で常時表示・アクセントカラー
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)

        self._run_btn = QPushButton("▶  実行")
        self._run_btn.setStatusTip("選択中の機能を実行")
        self._run_btn.setFixedHeight(32)
        self._run_btn.setMinimumWidth(110)
        self._run_btn.setStyleSheet("""
            QPushButton {
                background: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #33ddff;
            }
            QPushButton:pressed {
                background: #0099bb;
                color: #ffffff;
            }
        """)
        self._run_btn.clicked.connect(lambda: self.run_requested.emit(self._current_mode))
        self.addWidget(self._run_btn)

    def _on_mode_selected(self, mode_id: str):
        self._current_mode = mode_id
        labels = {
            "bg_remove":     "▶  背景除去",
            "select_remove": "▶  選択除去",
            "inpaint":       "▶  生成塗りつぶし",
            "upscale":       "▶  高解像度化",
        }
        self._run_btn.setText(labels.get(mode_id, "▶  実行"))
        self.mode_changed.emit(mode_id)
