"""Windows-style progress ring: five dots chasing each other around a circle.

The dots slow down near the top and speed through the bottom, so they bunch
up and spread out like the native Windows sign-in animation. Purely
decorative; it does not perform any real work.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QElapsedTimer, QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class Spinner(QWidget):
    """Lightweight indeterminate progress ring (no GIF assets needed)."""

    DOTS = 5
    PERIOD = 2.0     # seconds per lap
    DOT_DELAY = 0.065  # phase lag between consecutive dots

    def __init__(self, diameter: int = 36, parent: QWidget | None = None):
        super().__init__(parent)
        self._diameter = diameter
        self.setFixedSize(diameter, diameter)
        self._clock = QElapsedTimer()
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60fps
        self._timer.timeout.connect(self.update)

    def start(self) -> None:
        self._clock.start()
        self._timer.start()
        self.update()

    def stop(self) -> None:
        self._timer.stop()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        if not self._timer.isActive():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))

        dot_r = max(1.5, self._diameter * 0.055)
        orbit = self._diameter / 2 - dot_r - 1
        center = QPointF(self._diameter / 2, self._diameter / 2)
        t = self._clock.elapsed() / 1000.0

        for i in range(self.DOTS):
            phase = (t / self.PERIOD - i * self.DOT_DELAY) % 1.0
            # Non-linear sweep: slow at the top, fast through the bottom.
            angle = 360 * phase - 50 * math.sin(2 * math.pi * phase)
            theta = math.radians(angle - 90)
            painter.drawEllipse(
                center + QPointF(orbit * math.cos(theta), orbit * math.sin(theta)),
                dot_r, dot_r,
            )
        painter.end()
