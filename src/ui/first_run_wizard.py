from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox,
    QDialogButtonBox, QGroupBox,
)
from pathlib import Path

_SETTINGS_FILE = Path.home() / ".local_ai_editor" / "settings.json"


def should_show_wizard() -> bool:
    return not _SETTINGS_FILE.exists()


def mark_wizard_done():
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text('{"first_run_done": true}')


class FirstRunWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ローカルAI画像エディタ — 初回セットアップ")
        self.setMinimumWidth(500)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        title = QLabel("ようこそ！")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel(
            "このアプリはローカルAIで画像編集を行います。\n"
            "機能ごとに必要なモデルとインストール方法を確認してください。"
        ))

        for name, size, pip_cmd, desc in [
            (
                "背景除去（U²-Net）",
                "約 170 MB",
                "pip install onnxruntime",
                "自動背景除去・選択除去で使用",
            ),
            (
                "高解像度化（Real-ESRGAN）",
                "約 64 MB",
                "pip install realesrgan basicsr",
                "画像を4倍拡大する場合に使用（なくても動作）",
            ),
            (
                "生成塗りつぶし（Stable Diffusion Inpaint）",
                "約 4 GB",
                "pip install diffusers transformers accelerate torch",
                "AI生成塗りつぶしで使用（なければOpenCVフォールバック）",
            ),
        ]:
            box = QGroupBox(name)
            bl = QVBoxLayout(box)
            bl.addWidget(QLabel(f"サイズ: {size}"))
            bl.addWidget(QLabel(f"インストール: {pip_cmd}"))
            note = QLabel(desc)
            note.setStyleSheet("color: gray; font-size: 11px;")
            bl.addWidget(note)
            layout.addWidget(box)

        self._skip_cb = QCheckBox("次回から表示しない")
        self._skip_cb.setChecked(True)
        layout.addWidget(self._skip_cb)

        btn = QDialogButtonBox(QDialogButtonBox.Ok)
        btn.accepted.connect(self._on_ok)
        layout.addWidget(btn)

    def _on_ok(self):
        if self._skip_cb.isChecked():
            mark_wizard_done()
        self.accept()
