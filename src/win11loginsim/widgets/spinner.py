"""A small rotating-arc loading spinner, drawn with QPainter.

Mirrors the subtle ring animation Windows shows while "signing you in".
Purely decorative; it does not perform any real work.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class Spinner(QWidget):
    """Lightweight indeterminate spinner (no QMovie/gif assets needed)."""

    def __init__(self, diameter: int = 28, parent: QWidget | None = None):
        super().__init__(parent)
        self._diameter = diameter
        self._angle = 0
        self.setFixedSize(diameter, diameter)
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # ~60fps
        self._timer.timeout.connect(self._tick)
        self.hide()

    def _tick(self) -> None:
        self._angle = (self._angle + 6) % 360
        self.update()

    def start(self) -> None:
        self.show()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen_width = max(2, self._diameter // 10)
        rect = QRectF(
            pen_width, pen_width,
            self._diameter - 2 * pen_width,
            self._diameter - 2 * pen_width,
        )

        track_pen = QPen(QColor(255, 255, 255, 40))
        track_pen.setWidth(pen_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        arc_pen = QPen(QColor(255, 255, 255, 230))
        arc_pen.setWidth(pen_width)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(arc_pen)
        span = 110
        painter.drawArc(rect, -self._angle * 16, span * 16)
        painter.end()
