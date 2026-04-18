from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QDialogButtonBox,
)


class InpaintDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("生成塗りつぶし — 設定")
        self.setMinimumWidth(420)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("プロンプト（何を生成するか）:"))
        self._prompt = QLineEdit()
        self._prompt.setPlaceholderText("例: green grass, nature background")
        layout.addWidget(self._prompt)

        layout.addWidget(QLabel("ネガティブプロンプト（除外したいもの）:"))
        self._neg = QLineEdit()
        self._neg.setPlaceholderText("例: blurry, low quality")
        layout.addWidget(self._neg)

        brush_row = QHBoxLayout()
        brush_row.addWidget(QLabel("ブラシサイズ:"))
        self._brush_size = QSpinBox()
        self._brush_size.setRange(5, 200)
        self._brush_size.setValue(20)
        self._brush_size.setSuffix(" px")
        brush_row.addWidget(self._brush_size)
        brush_row.addStretch()
        layout.addLayout(brush_row)

        note = QLabel(
            "※ diffusers + SDモデル未インストール時は OpenCV で塗りつぶします。\n"
            "AI生成を使うには: pip install diffusers transformers accelerate"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(note)

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
    def brush_size(self) -> int:
        return self._brush_size.value()
