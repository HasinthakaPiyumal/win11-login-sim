"""Surprise screen shown after the simulated sign-in succeeds.

Displays the configured message, a soft reveal animation, an optional
countdown, and a small always-visible reminder of the recovery shortcut (the
app never traps the user — ``Ctrl+Shift+Q`` always closes it, enforced in
``app.py`` regardless of what this screen does).
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget

from ..config import Config
from ..theme import font


class SurpriseScreen(QWidget):
    """Final screen: the reveal message plus optional decorative countdown."""

    def __init__(self, wallpaper, cfg: Config, parent: QWidget | None = None):
        super().__init__(parent)
        self._wallpaper = wallpaper
        self.cfg = cfg
        self._remaining = max(0, int(cfg.countdown_seconds))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addStretch(3)

        self.title_label = QLabel(cfg.surprise_title, self)
        self.title_label.setFont(font(44))
        self.title_label.setStyleSheet("color: white; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(cfg.surprise_subtitle, self)
        self.subtitle_label.setFont(font(20))
        self.subtitle_label.setStyleSheet(
            "color: rgba(255,255,255,0.85); background: transparent;"
        )
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addSpacing(10)
        layout.addWidget(self.subtitle_label)

        self.countdown_label = QLabel("", self)
        self.countdown_label.setFont(font(16))
        self.countdown_label.setStyleSheet(
            "color: rgba(255,255,255,0.7); background: transparent;"
        )
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(18)
        layout.addWidget(self.countdown_label)

        layout.addStretch(3)

        self.hint_label = QLabel(
            "Press Ctrl+Shift+Q at any time to close this simulation", self
        )
        self.hint_label.setFont(font(12))
        self.hint_label.setStyleSheet(
            "color: rgba(255,255,255,0.55); background: transparent;"
        )
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.hint_label)

        self.setLayout(layout)

        self._fade_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._fade_effect)
        self._fade_anim = QPropertyAnimation(self._fade_effect, b"opacity", self)
        self._fade_anim.setDuration(600)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def on_shown(self) -> None:
        """Called when this screen becomes visible; (re)starts the reveal."""
        self._fade_anim.start()
        self._remaining = max(0, int(self.cfg.countdown_seconds))
        if self._remaining > 0:
            self._update_countdown_text()
            self._timer.start()
        else:
            self.countdown_label.setText("")

    def _tick(self) -> None:
        self._remaining -= 1
        if self._remaining <= 0:
            self._timer.stop()
            self.countdown_label.setText("Whenever you're ready ✨")
            return
        self._update_countdown_text()

    def _update_countdown_text(self) -> None:
        self.countdown_label.setText(f"Access opens in {self._remaining}s")

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        if not self._wallpaper.isNull():
            scaled = self._wallpaper.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))
        painter.end()
        super().paintEvent(event)
