"""Windows-11-style lock screen: wallpaper, clock, date, "press any key" hint.

Clicking anywhere or pressing any key advances to the login screen, matching
real Windows lock-screen behaviour (this is purely a UI transition; no input
hook is installed, Qt simply receives events normally sent to this window).
"""

from __future__ import annotations

from PySide6.QtCore import QDateTime, Qt, QTimer, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..config import Config
from ..theme import Palette, font


class LockScreen(QWidget):
    """First screen shown: wallpaper + clock, waiting for any input."""

    advance_requested = Signal()

    def __init__(self, wallpaper, cfg: Config, parent: QWidget | None = None):
        super().__init__(parent)
        self._wallpaper = wallpaper
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(3)

        if cfg.show_clock:
            self.time_label = QLabel(self)
            self.time_label.setFont(font(72))
            self.time_label.setStyleSheet("color: white; background: transparent;")
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            self.date_label = QLabel(self)
            self.date_label.setFont(font(20))
            self.date_label.setStyleSheet(
                "color: rgba(255,255,255,0.85); background: transparent;"
            )
            self.date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            layout.addWidget(self.time_label)
            layout.addWidget(self.date_label)

            self._clock_timer = QTimer(self)
            self._clock_timer.setInterval(1000)
            self._clock_timer.timeout.connect(self._update_clock)
            self._clock_timer.start()
            self._update_clock()
        else:
            self.time_label = None
            self.date_label = None

        layout.addStretch(2)

        hint = QLabel("Click anywhere or press any key to continue", self)
        hint.setFont(font(14))
        hint.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(hint)
        layout.addSpacing(40)

        self.setLayout(layout)

    def _update_clock(self) -> None:
        if self.time_label is None:
            return
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("h:mm"))
        self.date_label.setText(now.toString("dddd, MMMM d"))

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
        painter.end()
        super().paintEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.advance_requested.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.advance_requested.emit()
        super().keyPressEvent(event)
