from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QEvent, QTimer, Qt, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
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
        self.video_widget.setStyleSheet("background: black;")
        self.video_widget.setMouseTracking(True)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.player.setVideoOutput(self.video_widget)

        # Controls overlay (true-ish media controls; styled later)
        # Important: make controls a CHILD of video_widget so they stack above
        # the video even when QVideoWidget is a native surface on Windows.
        self.controls = QWidget(self.video_widget)
        self.controls.setStyleSheet(
            "background: rgba(255,255,255,230); border: 1px solid rgba(0,0,0,60); border-radius: 12px;"
        )
        self.controls.setVisible(False)

        self.btn_play = QPushButton("⏵", self.controls)
        self.btn_pause = QPushButton("⏸", self.controls)
        self.btn_mute = QPushButton("🔇", self.controls)
        self.lbl_time = QLabel("0:00 / 0:00", self.controls)
        self.slider = QSlider(Qt.Orientation.Horizontal, self.controls)
        self.btn_close = QPushButton("✕", self.controls)

        self.btn_close.setToolTip("Close (Esc)")
        self.btn_play.setToolTip("Play")
        self.btn_pause.setToolTip("Pause")
        self.btn_mute.setToolTip("Mute")

        self.slider.setRange(0, 0)
        self.slider.setSingleStep(1000)
        self.slider.setPageStep(5000)

        for b in (self.btn_play, self.btn_pause, self.btn_mute, self.btn_close):
            b.setStyleSheet(
                "color: rgba(0,0,0,230); background: transparent; border: none; padding: 6px 10px; font-size: 16px;"
            )
        self.lbl_time.setStyleSheet("color: rgba(0,0,0,180); font-size: 12px;")
        self.slider.setStyleSheet("min-width: 260px;")

        self.btn_play.clicked.connect(self.player.play)
        self.btn_pause.clicked.connect(self.player.pause)
        self.btn_close.clicked.connect(self.close_overlay)
        self.btn_mute.clicked.connect(self._toggle_mute)

        self.slider.sliderPressed.connect(self._on_seek_start)
        self.slider.sliderReleased.connect(self._on_seek_commit)

        c_layout = QHBoxLayout(self.controls)
        c_layout.setContentsMargins(12, 8, 12, 8)
        c_layout.setSpacing(10)
        c_layout.addWidget(self.btn_play)
        c_layout.addWidget(self.btn_pause)
        c_layout.addWidget(self.btn_mute)
        c_layout.addWidget(self.slider, 1)
        c_layout.addWidget(self.lbl_time)
        c_layout.addWidget(self.btn_close)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.backdrop, 1)
        layout.addWidget(self.video_widget, 0)

        # Put the video surface above the backdrop using stacking
        self.backdrop.lower()
        self.video_widget.raise_()
        self.controls.raise_()

        # Track seek state
        self._seeking = False

        # Auto-hide controls (we'll keep them visible longer; some Windows video
        # surfaces don't reliably emit mouse move events)
        self._hide_timer = QTimer(self)
        self._hide_timer.setInterval(6000)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_controls)

        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.playbackStateChanged.connect(lambda _s: self._show_controls())

        # Clicking backdrop closes
        self.backdrop.installEventFilter(self)

        # Show controls when mouse moves over the video surface
        self.video_widget.installEventFilter(self)
        self.controls.installEventFilter(self)

        # ESC closes reliably
        QShortcut(QKeySequence("Escape"), self, activated=self.close_overlay)

        # Track looping
        self._loop = False
        self.player.mediaStatusChanged.connect(self._on_media_status)

    def eventFilter(self, obj, event) -> bool:  # type: ignore[override]
        if obj is self.backdrop and event.type() == QEvent.Type.MouseButtonPress:
            self.close_overlay()
            return True
        if event.type() in (QEvent.Type.MouseMove, QEvent.Type.HoverMove):
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

        # Controls bottom overlay (centered) — coordinates relative to video_widget
        self.controls.adjustSize()
        x = (self.video_widget.width() // 2) - (self.controls.width() // 2)
        y = self.video_widget.height() - self.controls.height() - 12
        self.controls.move(max(12, x), max(12, y))

        # Keep stacking order consistent
        self.backdrop.lower()
        self.video_widget.raise_()
        self.controls.raise_()

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

        # Force controls visible on open; auto-hide after a while.
        self._show_controls()
        QTimer.singleShot(0, self.controls.raise_)

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

    def _format_ms(self, ms: int) -> str:
        s = max(0, int(ms // 1000))
        m = s // 60
        s = s % 60
        if m >= 60:
            h = m // 60
            m = m % 60
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _on_duration(self, dur: int) -> None:
        self.slider.setRange(0, max(0, int(dur)))
        self._on_position(self.player.position())

    def _on_position(self, pos: int) -> None:
        if not self._seeking:
            self.slider.setValue(int(pos))
        self.lbl_time.setText(
            f"{self._format_ms(int(pos))} / {self._format_ms(int(self.player.duration()))}"
        )

    def _on_seek_start(self) -> None:
        self._seeking = True
        self._show_controls()

    def _on_seek_commit(self) -> None:
        try:
            self.player.setPosition(int(self.slider.value()))
        except Exception:
            pass
        self._seeking = False
        self._show_controls()

    def _toggle_mute(self) -> None:
        m = not self.audio.isMuted()
        self.audio.setMuted(m)
        self.btn_mute.setText("🔇" if m else "🔊")
        self._show_controls()

    def _show_controls(self) -> None:
        self.controls.setVisible(True)
        self.controls.raise_()
        self._hide_timer.start()

    def _hide_controls(self) -> None:
        # Don't hide while seeking.
        if self._seeking:
            self._hide_timer.start()
            return
        self.controls.setVisible(False)
