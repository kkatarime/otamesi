import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QSizePolicy, QFrame
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QFont


def _format_ms(ms: int) -> str:
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class MediaPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._seeking = False
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._build_video_area())
        layout.addLayout(self._build_seek_row())
        layout.addLayout(self._build_controls_row())

    def _build_video_area(self) -> QWidget:
        self._video = QVideoWidget()
        self._video.setMinimumHeight(300)
        self._video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._video.setStyleSheet("background: #1a1a1a;")
        self._player.setVideoOutput(self._video)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._video)

        self._title_label = QLabel("ファイルを選択してください")
        self._title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self._title_label.setFont(font)
        vbox.addWidget(self._title_label)
        return container

    def _build_seek_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self._pos_label = QLabel("0:00")
        self._seek_slider = QSlider(Qt.Horizontal)
        self._seek_slider.setRange(0, 0)
        self._dur_label = QLabel("0:00")
        row.addWidget(self._pos_label)
        row.addWidget(self._seek_slider, 1)
        row.addWidget(self._dur_label)
        return row

    def _build_controls_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        self._prev_btn = QPushButton("⏮")
        self._play_btn = QPushButton("▶")
        self._stop_btn = QPushButton("⏹")
        self._next_btn = QPushButton("⏭")
        for btn in (self._prev_btn, self._play_btn, self._stop_btn, self._next_btn):
            btn.setFixedSize(44, 36)
            row.addWidget(btn)
        row.addStretch()
        self._vol_slider = QSlider(Qt.Horizontal)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(70)
        self._vol_slider.setFixedWidth(100)
        row.addWidget(QLabel("🔊"))
        row.addWidget(self._vol_slider)
        return row

    def _connect_signals(self):
        self._play_btn.clicked.connect(self._toggle_play)
        self._stop_btn.clicked.connect(self._stop)
        self._vol_slider.valueChanged.connect(self._player.setVolume)
        self._player.setVolume(70)

        self._seek_slider.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self._seek_slider.sliderReleased.connect(self._on_seek_released)

        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.stateChanged.connect(self._on_state_changed)

    def load(self, file_path: str):
        url = QUrl.fromLocalFile(file_path)
        self._player.setMedia(QMediaContent(url))
        self._player.play()
        self._title_label.setText(os.path.basename(file_path))

    def _toggle_play(self):
        if self._player.state() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _stop(self):
        self._player.stop()

    def _on_seek_released(self):
        self._seeking = False
        self._player.setPosition(self._seek_slider.value())

    def _on_position_changed(self, pos: int):
        if not self._seeking:
            self._seek_slider.setValue(pos)
        self._pos_label.setText(_format_ms(pos))

    def _on_duration_changed(self, dur: int):
        self._seek_slider.setRange(0, dur)
        self._dur_label.setText(_format_ms(dur))

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self._play_btn.setText("⏸")
        else:
            self._play_btn.setText("▶")
