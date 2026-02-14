from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QEvent, QTimer, Qt, QUrl
from PySide6.QtGui import QKeySequence
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QShortcut,
)


@dataclass(frozen=True)
class VideoRequest:
    path: str
    autoplay: bool
    loop: bool
    muted: bool


class LightboxVideoOverlay(QWidget):
    """Native video overlay that sits above the WebEngine view.

    Rationale: QtWebEngine video codec support can be unreliable on Windows.
    We render the *lightbox chrome* in the web UI, but render the video itself
    with QtMultimedia so playback works.

    This widget is designed to cover the WebEngine viewport.

    Signals are kept minimal: callers can observe close to sync the web layer.
    """

    # Caller can connect to this to close the web lightbox chrome.
    # (We avoid importing Signal here to keep this file simple; use callback pattern.)

    def __init__(self, *, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setVisible(False)

        # Optional close callback (set by owner)
        self.on_close = None

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)

        self.backdrop = QFrame(self)
        self.backdrop.setStyleSheet("background: rgba(0,0,0,190);")

        self.video_widget = QVideoWidget(self)
        self.video_widget.setMouseTracking(True)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.player.setVideoOutput(self.video_widget)

        # Controls overlay (minimal first pass)
        self.controls = QWidget(self)
        self.controls.setStyleSheet(
            "background: rgba(20,20,25,160); border: 1px solid rgba(255,255,255,40); border-radius: 10px;"
        )
        self.controls.setVisible(False)

        self.btn_play = QPushButton("⏵", self.controls)
        self.btn_pause = QPushButton("⏸", self.controls)
        self.btn_close = QPushButton("✕", self.controls)

        self.btn_close.setToolTip("Close (Esc)")

        for b in (self.btn_play, self.btn_pause, self.btn_close):
            b.setStyleSheet(
                "color: rgba(255,255,255,230); background: transparent; border: none; padding: 6px 10px; font-size: 16px;"
            )

        self.btn_play.clicked.connect(self.player.play)
        self.btn_pause.clicked.connect(self.player.pause)
        self.btn_close.clicked.connect(self.close_overlay)

        c_layout = QHBoxLayout(self.controls)
        c_layout.setContentsMargins(10, 6, 10, 6)
        c_layout.setSpacing(10)
        c_layout.addWidget(self.btn_play)
        c_layout.addWidget(self.btn_pause)
        c_layout.addStretch(1)
        c_layout.addWidget(self.btn_close)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.backdrop, 1)

        # Put the video widget above the backdrop using stacking
        self.backdrop.lower()
        self.video_widget.raise_()
        self.controls.raise_()

        # Auto-hide controls
        self._hide_timer = QTimer(self)
        self._hide_timer.setInterval(1200)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_controls)

        # Clicking backdrop closes
        self.backdrop.installEventFilter(self)

        # Show controls when mouse moves over the video surface
        self.video_widget.installEventFilter(self)

        # ESC closes reliably
        QShortcut(QKeySequence("Escape"), self, activated=self.close_overlay)

        # Track looping
        self._loop = False
        self.player.mediaStatusChanged.connect(self._on_media_status)

    def eventFilter(self, obj, event) -> bool:  # type: ignore[override]
        if obj is self.backdrop and event.type() == QEvent.Type.MouseButtonPress:
            self.close_overlay()
            return True
        if obj is self.video_widget and event.type() == QEvent.Type.MouseMove:
            self._show_controls()
        return super().eventFilter(obj, event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        self._show_controls()
        super().mouseMoveEvent(event)

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._show_controls()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._hide_timer.start()
        super().leaveEvent(event)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_Escape:
            self.close_overlay()
            event.accept()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self.backdrop.setGeometry(self.rect())

        # Fit video in viewport with padding (like the web lightbox)
        pad = 20
        r = self.rect().adjusted(pad, pad, -pad, -pad)
        self.video_widget.setGeometry(r)

        # Controls top-right overlay
        self.controls.adjustSize()
        self.controls.move(r.right() - self.controls.width(), r.top())

    def open_video(self, req: VideoRequest) -> None:
        path = str(Path(req.path))
        self._loop = bool(req.loop)
        self.audio.setMuted(bool(req.muted))

        # Looping support varies by Qt version.
        if hasattr(self.player, "setLoops"):
            try:
                self.player.setLoops(-1 if req.loop else 1)  # type: ignore[attr-defined]
            except Exception:
                pass

        self.player.setSource(QUrl.fromLocalFile(path))
        self.setVisible(True)
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self.video_widget.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

        if req.autoplay:
            self.player.play()
        else:
            self.player.pause()

        self._show_controls()

    def close_overlay(self) -> None:
        try:
            self.player.stop()
        except Exception:
            pass
        self.setVisible(False)
        if callable(self.on_close):
            try:
                self.on_close()
            except Exception:
                pass

    def _on_media_status(self, status) -> None:
        # Fallback looping if setLoops isn't available.
        if not self._loop:
            return
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def _show_controls(self) -> None:
        self.controls.setVisible(True)
        self._hide_timer.start()

    def _hide_controls(self) -> None:
        self.controls.setVisible(False)
