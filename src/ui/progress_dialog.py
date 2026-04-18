from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal


class ProgressDialog(QDialog):
    cancel_requested = pyqtSignal()

    def __init__(self, message: str, parent=None, cancelable: bool = False):
        super().__init__(parent)
        self.setWindowTitle("処理中")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(360, 120)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self._label = QLabel(message)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        bar = QProgressBar()
        bar.setRange(0, 0)
        layout.addWidget(bar)

        if cancelable:
            btn = QPushButton("キャンセル")
            btn.clicked.connect(self._on_cancel)
            layout.addWidget(btn)

        self._cancelled = False

    def set_message(self, message: str):
        self._label.setText(message)

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def _on_cancel(self):
        self._cancelled = True
        self.cancel_requested.emit()
        self.reject()
