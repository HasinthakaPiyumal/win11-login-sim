"""Shared base for full-screen views drawn over a background image."""

from __future__ import annotations

from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from ..assets import cover_scaled
from ..theme import Scale


class BackgroundScreen(QWidget):
    """Paints a cover-scaled background, then ``paint_overlay`` on top.

    The scaled background is cached per size so repaints (animations) only
    blit a pixmap.
    """

    def __init__(self, background: QPixmap, px: Scale, parent: QWidget | None = None):
        super().__init__(parent)
        self.px = px
        self._background = background
        self._scaled = QPixmap()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._scaled = cover_scaled(self._background, self.size(), self.devicePixelRatioF())
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        if not self._scaled.isNull():
            painter.drawPixmap(0, 0, self._scaled)
        self.paint_overlay(painter)
        painter.end()

    def paint_overlay(self, painter: QPainter) -> None:
        """Hook for subclasses to draw above the background."""
