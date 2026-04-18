import sys

# PyQt5より先にtorchをロードしないとWindows DLL競合が発生するため先読みする
try:
    import torch  # noqa: F401
except (ImportError, OSError):
    pass

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.theme import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ローカルAI画像エディタ")
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
