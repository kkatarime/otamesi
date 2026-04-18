"""ミッドナイトブルー テーマ定義"""

BG       = "#0d1b2a"
BG_PANEL = "#112236"
BG_CARD  = "#0f2030"
CANVAS   = "#071018"
ACCENT   = "#00d4ff"
ACCENT2  = "#0099bb"
TEXT     = "#e0f0ff"
TEXT_DIM = "#7aa0c0"
BORDER   = "#1e3a5a"
SUCCESS  = "#00c97a"
WARNING  = "#f0a030"

STYLESHEET = f"""
QMainWindow, QDialog {{
    background: {BG};
    color: {TEXT};
}}

QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}}

QToolBar {{
    background: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
    spacing: 4px;
    padding: 4px 8px;
}}

QToolBar QToolButton {{
    background: transparent;
    color: {TEXT};
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 13px;
}}

QToolBar QToolButton:hover {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
}}

QToolBar QToolButton:checked {{
    background: {ACCENT2};
    color: #ffffff;
    border: 1px solid {ACCENT};
}}

QToolBar::separator {{
    background: {BORDER};
    width: 1px;
    margin: 4px 6px;
}}

QStatusBar {{
    background: {BG_PANEL};
    color: {TEXT_DIM};
    border-top: 1px solid {BORDER};
    font-size: 12px;
}}

QLabel {{
    background: transparent;
    color: {TEXT};
}}

QPushButton {{
    background: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 14px;
    font-size: 13px;
}}

QPushButton:hover {{
    background: {BORDER};
    border-color: {ACCENT};
    color: {ACCENT};
}}

QPushButton:pressed {{
    background: {ACCENT2};
    color: #ffffff;
}}

QDialogButtonBox QPushButton[text="OK"] {{
    background: {ACCENT2};
    color: #ffffff;
    border: 1px solid {ACCENT};
    font-weight: bold;
}}

QDialogButtonBox QPushButton[text="OK"]:hover {{
    background: {ACCENT};
    color: #000000;
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
    background: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: {ACCENT2};
    selection-color: #ffffff;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {BORDER};
    border: none;
    width: 16px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {ACCENT2};
}}

QProgressBar {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT};
    height: 14px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT2}, stop:1 {ACCENT});
    border-radius: 3px;
}}

QScrollArea {{
    background: {BG};
    border: none;
}}

QScrollBar:vertical {{
    background: {BG_CARD};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {ACCENT2};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {BG_CARD};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {ACCENT2};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    background: {BORDER};
    border: none;
    max-height: 1px;
}}

QMessageBox {{
    background: {BG};
    color: {TEXT};
}}

QMessageBox QLabel {{
    color: {TEXT};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}
"""
