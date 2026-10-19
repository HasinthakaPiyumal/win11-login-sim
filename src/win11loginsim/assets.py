"""Runtime-generated visual assets.

Everything here is drawn procedurally with QPainter so the project ships with
zero bundled image binaries (no licensing questions, no internet download at
runtime) while still looking like a polished, modern background and avatar.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
    QRadialGradient,
)

from .theme import Palette, font


def make_wallpaper(size, accent_hex: str = "#0067C0") -> QPixmap:
    """Generate a Windows-11-style abstract "bloom" wallpaper.

    Draws soft overlapping radial blooms over a diagonal gradient, echoing the
    look of the stock Windows 11 background without reproducing it.
    """
    w, h = max(size.width(), 1), max(size.height(), 1)
    pix = QPixmap(w, h)
    pix.fill(QColor("#0b1b2b"))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    base = QLinearGradient(0, 0, w, h)
    base.setColorAt(0.0, QColor("#0a1a2f"))
    base.setColorAt(0.5, QColor("#133a5e"))
    base.setColorAt(1.0, QColor("#1c5c86"))
    painter.fillRect(0, 0, w, h, QBrush(base))

    accent = Palette.accent(accent_hex)
    blooms = [
        (0.18, 0.22, 0.55, QColor(accent.red(), accent.green(), accent.blue(), 120)),
        (0.80, 0.15, 0.40, QColor(255, 255, 255, 40)),
        (0.70, 0.80, 0.60, QColor(10, 80, 140, 160)),
        (0.25, 0.85, 0.45, QColor(90, 190, 230, 90)),
    ]
    for rel_x, rel_y, rel_r, color in blooms:
        cx, cy = w * rel_x, h * rel_y
        radius = max(w, h) * rel_r
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0.0, color)
        transparent = QColor(color)
        transparent.setAlpha(0)
        grad.setColorAt(1.0, transparent)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    # Subtle vignette so foreground text stays legible everywhere.
    vignette = QRadialGradient(w / 2, h * 0.55, max(w, h) * 0.8)
    vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
    vignette.setColorAt(1.0, QColor(0, 0, 0, 110))
    painter.setBrush(QBrush(vignette))
    painter.drawRect(0, 0, w, h)

    painter.end()
    return pix


def make_avatar(diameter: int, initials: str, accent_hex: str = "#0067C0") -> QPixmap:
    """Generate a circular avatar with initials, mimicking the Win11 account tile."""
    pix = QPixmap(diameter, diameter)
    pix.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    path = QPainterPath()
    path.addEllipse(QRectF(0, 0, diameter, diameter))
    painter.setClipPath(path)

    accent = Palette.accent(accent_hex)
    grad = QLinearGradient(0, 0, diameter, diameter)
    grad.setColorAt(0.0, accent.lighter(115))
    grad.setColorAt(1.0, accent.darker(140))
    painter.fillRect(0, 0, diameter, diameter, QBrush(grad))

    painter.setPen(Palette.TEXT)
    label_font = font(int(diameter * 0.38), QFont.Weight.DemiBold)
    painter.setFont(label_font)
    painter.drawText(
        QRectF(0, 0, diameter, diameter),
        Qt.AlignmentFlag.AlignCenter,
        initials,
    )

    painter.setClipping(False)
    ring_pen = painter.pen()
    ring_pen.setColor(QColor(255, 255, 255, 60))
    ring_pen.setWidth(2)
    painter.setPen(ring_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QRectF(1, 1, diameter - 2, diameter - 2))

    painter.end()
    return pix
