from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QFrame,
)


def _ai_status() -> tuple[bool, str]:
    try:
        from ai.inpainter import is_diffusers_available, is_model_cached
        if not is_diffusers_available():
            return False, (
                "⚠️ AIモデル未インストール\n"
                "プロンプトは無視され、OpenCV（周囲ピクセル補完）で処理されます。\n"
                "AI生成: pip install diffusers transformers accelerate torch"
            )
        if not is_model_cached():
            return False, (
                "⚠️ SDモデル未ダウンロード（約4GB）\n"
                "プロンプトは無視されます。モデル取得後に再度お試しください。"
            )
        return True, "✅ AI生成モード（Stable Diffusion Inpaint）"
    except Exception:
        return False, "⚠️ 状態確認に失敗しました。OpenCVで処理します。"


def _row(label: str, widget) -> QHBoxLayout:
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setFixedWidth(140)
    row.addWidget(lbl)
    row.addWidget(widget)
    return row


class InpaintDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("生成塗りつぶし — 設定")
        self.setMinimumWidth(480)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        ai_ok, ai_msg = _ai_status()

        status = QLabel(ai_msg)
        status.setWordWrap(True)
        status.setStyleSheet(
            "background:#0a3020;color:#00c97a;padding:8px;border-radius:4px;border:1px solid #00c97a;" if ai_ok
            else "background:#2a1e00;color:#f0a030;padding:8px;border-radius:4px;border:1px solid #f0a030;"
        )
        layout.addWidget(status)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # プロンプト
        layout.addWidget(QLabel("プロンプト（何を生成するか）:"))
        self._prompt = QLineEdit()
        self._prompt.setPlaceholderText("例: flame, fire effect, glowing embers")
        self._prompt.setEnabled(ai_ok)
        layout.addWidget(self._prompt)

        layout.addWidget(QLabel("ネガティブプロンプト（除外したいもの）:"))
        self._neg = QLineEdit()
        self._neg.setPlaceholderText("空白=自動設定（blurry, artifacts...）")
        self._neg.setEnabled(ai_ok)
        layout.addWidget(self._neg)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        layout.addWidget(sep2)

        # 品質パラメータ
        self._steps = QSpinBox()
        self._steps.setRange(10, 80)
        self._steps.setValue(30)
        self._steps.setSuffix(" steps")
        self._steps.setToolTip("多いほど高品質・低速。CPU: 30≒90秒、50≒150秒")
        self._steps.setEnabled(ai_ok)
        layout.addLayout(_row("ステップ数（品質）:", self._steps))

        self._cfg = QDoubleSpinBox()
        self._cfg.setRange(1.0, 20.0)
        self._cfg.setValue(9.0)
        self._cfg.setSingleStep(0.5)
        self._cfg.setToolTip("高いほどプロンプトに忠実。7〜12が推奨")
        self._cfg.setEnabled(ai_ok)
        layout.addLayout(_row("Guidance Scale:", self._cfg))

        self._seed = QSpinBox()
        self._seed.setRange(-1, 2147483647)
        self._seed.setValue(-1)
        self._seed.setSpecialValueText("ランダム")
        self._seed.setToolTip("-1=毎回異なる結果。固定値で再現可能")
        self._seed.setEnabled(ai_ok)
        layout.addLayout(_row("シード値:", self._seed))

        sep3 = QFrame(); sep3.setFrameShape(QFrame.HLine)
        layout.addWidget(sep3)

        self._brush_size = QSpinBox()
        self._brush_size.setRange(5, 200)
        self._brush_size.setValue(20)
        self._brush_size.setSuffix(" px")
        layout.addLayout(_row("ブラシサイズ:", self._brush_size))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def set_defaults(self, prompt: str, negative_prompt: str):
        self._prompt.setText(prompt)
        self._neg.setText(negative_prompt)

    @property
    def prompt(self) -> str:
        return self._prompt.text().strip()

    @property
    def negative_prompt(self) -> str:
        return self._neg.text().strip()

    @property
    def steps(self) -> int:
        return self._steps.value()

    @property
    def guidance_scale(self) -> float:
        return self._cfg.value()

    @property
    def seed(self) -> int:
        return self._seed.value()

    @property
    def brush_size(self) -> int:
        return self._brush_size.value()
