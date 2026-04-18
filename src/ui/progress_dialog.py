from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt


class ProgressDialog(QDialog):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("処理中")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(320, 100)
        self.setModal(True)

        layout = QVBoxLayout(self)
        self._label = QLabel(message)
        self._label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label)

        bar = QProgressBar()
        bar.setRange(0, 0)  # インジケーター（無限）
        layout.addWidget(bar)

    def set_message(self, message: str):
        self._label.setText(message)
