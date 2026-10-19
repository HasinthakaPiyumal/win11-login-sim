"""Windows-11-style lock screen: wallpaper, large clock and date.

Clicking anywhere or pressing any key advances to the sign-in screen, as on
real Windows. A printable key is forwarded so it becomes the first typed
character. No input hook is installed; Qt only delivers events sent to this
window.
"""

from __future__ import annotations

from PySide6.QtCore import QDateTime, QLocale, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..config import Config
from ..theme import Glyph, Scale, font
from ..widgets.status_icons import StatusIcons
from .base import BackgroundScreen


def _time_format() -> str:
    """System short time format without AM/PM, as the lock screen shows it."""
    fmt = QLocale.system().timeFormat(QLocale.FormatType.ShortFormat)
    for token in ("AP", "ap", "A", "a"):
        fmt = fmt.replace(token, "")
    return fmt.strip() or "h:mm"


def _shadowed_label(parent: QWidget, px: Scale, size: int, weight: QFont.Weight) -> QLabel:
    label = QLabel(parent)
    label.setFont(font(px(size), weight))
    label.setStyleSheet("color: white;")
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    shadow = QGraphicsDropShadowEffect(label)
    shadow.setBlurRadius(px(24))
    shadow.setOffset(0, px(2))
    shadow.setColor(QColor(0, 0, 0, 80))
    label.setGraphicsEffect(shadow)
    return label


class LockScreen(BackgroundScreen):
    """First screen shown: wallpaper + clock, waiting for any input."""

    advance_requested = Signal(str)

    def __init__(self, wallpaper: QPixmap, cfg: Config, px: Scale, parent: QWidget | None = None):
        super().__init__(wallpaper, px, parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._time_format = _time_format()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(px(24), 0, px(24), px(20))
        layout.setSpacing(0)
        layout.addStretch(1)

        self.time_label = self.date_label = None
        if cfg.show_clock:
            self.time_label = _shadowed_label(self, px, 120, QFont.Weight.DemiBold)
            self.date_label = _shadowed_label(self, px, 24, QFont.Weight.Medium)
            layout.addWidget(self.time_label)
            layout.addSpacing(px(2))
            layout.addWidget(self.date_label)

            self._clock_timer = QTimer(self)
            self._clock_timer.setInterval(1000)
            self._clock_timer.timeout.connect(self._update_clock)
            self._clock_timer.start()
            self._update_clock()

        layout.addStretch(6)

        status = QHBoxLayout()
        status.addStretch(1)
        status.addWidget(StatusIcons((Glyph.WIFI, Glyph.BATTERY), px, self))
        layout.addLayout(status)

    def _update_clock(self) -> None:
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString(self._time_format))
        self.date_label.setText(QLocale.system().toString(now.date(), "dddd, MMMM d"))

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.advance_requested.emit("")
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        text = event.text()
        blocked = (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        typed = ""
        if text.strip() and text.isprintable() and not (event.modifiers() & blocked):
            typed = text
        self.advance_requested.emit(typed)
        super().keyPressEvent(event)
