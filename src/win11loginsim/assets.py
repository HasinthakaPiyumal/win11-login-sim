"""Runtime-generated visual assets.

Everything here is drawn procedurally with QPainter so the project ships with
zero bundled image binaries (no licensing questions, no internet download at
runtime) while still looking like a polished, modern background and avatar.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene

from .theme import Palette, font


def _petal(length: float, width: float) -> QPainterPath:
    """A leaf-shaped petal whose base sits at the origin, pointing up."""
    path = QPainterPath(QPointF(0, 0))
    path.cubicTo(width * 0.9, -length * 0.18, width * 0.75, -length * 0.8, 0, -length)
    path.cubicTo(-width * 0.75, -length * 0.8, -width * 0.9, -length * 0.18, 0, 0)
    return path


def make_wallpaper(width: int, height: int, accent_hex: str = "#0067C0") -> QPixmap:
    """Generate an original abstract "bloom" wallpaper at the given pixel size.

    Layered translucent petals over a deep gradient, tinted by the accent
    colour, in the spirit of the Windows 11 default background.
    """
    w, h = max(width, 1), max(height, 1)
    image = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    hue = Palette.accent(accent_hex).hsvHueF()
    if hue < 0:
        hue = 0.57

    def tone(s: float, v: float, a: float = 1.0, shift: float = 0.0) -> QColor:
        return QColor.fromHsvF((hue + shift) % 1.0, s, v, a)

    background = QLinearGradient(0, 0, 0, h)
    background.setColorAt(0.0, tone(0.70, 0.42))
    background.setColorAt(0.55, tone(0.85, 0.24))
    background.setColorAt(1.0, tone(0.92, 0.10))
    painter.fillRect(0, 0, w, h, background)

    haze = QRadialGradient(w * 0.15, 0, max(w, h) * 0.9)
    haze.setColorAt(0.0, tone(0.30, 1.0, 0.22))
    haze.setColorAt(1.0, tone(0.30, 1.0, 0.0))
    painter.fillRect(0, 0, w, h, haze)

    cx, cy = w * 0.5, h * 0.58
    size = min(w, h * 1.3) * 0.46

    aura = QRadialGradient(cx, cy, size * 1.4)
    aura.setColorAt(0.0, tone(0.75, 0.95, 0.45))
    aura.setColorAt(1.0, tone(0.75, 0.95, 0.0))
    painter.fillRect(0, 0, w, h, aura)

    edge_pen = QPen(QColor(255, 255, 255, 60), max(1.0, size * 0.004))
    layers = [
        # (angle offset, lengths, width ratio, base colour, tip colour, mode)
        (30, (1.0, 0.86, 0.95, 0.82, 0.92, 0.88), 0.44,
         tone(0.95, 0.50, 0.85), tone(0.70, 0.95, 0.50, -0.02),
         QPainter.CompositionMode.CompositionMode_SourceOver),
        (0, (0.84, 0.76, 0.8, 0.72, 0.82, 0.74), 0.38,
         tone(0.90, 0.80, 0.95), tone(0.35, 1.0, 0.75, 0.02),
         QPainter.CompositionMode.CompositionMode_Screen),
    ]
    for offset, lengths, width_ratio, base, tip, mode in layers:
        painter.setCompositionMode(mode)
        for i, rel_len in enumerate(lengths):
            length = size * rel_len
            path = _petal(length, length * width_ratio)
            grad = QLinearGradient(0, 0, 0, -length)
            grad.setColorAt(0.0, base)
            grad.setColorAt(1.0, tip)
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(offset + i * 60)
            painter.fillPath(path, grad)
            painter.strokePath(path, edge_pen)
            painter.restore()

    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
    glow = QRadialGradient(cx, cy, size * 0.4)
    glow.setColorAt(0.0, QColor(255, 255, 255, 170))
    glow.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.fillRect(0, 0, w, h, glow)

    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
    vignette = QRadialGradient(w / 2, h * 0.55, max(w, h) * 0.85)
    vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
    vignette.setColorAt(1.0, QColor(0, 0, 0, 120))
    painter.fillRect(0, 0, w, h, vignette)

    painter.end()
    return QPixmap.fromImage(image)


def blur_pixmap(source: QPixmap, radius: float) -> QPixmap:
    """Return a heavily blurred copy of ``source`` (acrylic-style backdrop).

    The image is blurred at quarter resolution for speed and padded with its
    own stretched content so the edges don't fade to transparent.
    """
    if source.isNull():
        return QPixmap()
    factor = 4
    sw, sh = max(1, source.width() // factor), max(1, source.height() // factor)
    r = max(1.0, radius / factor)
    margin = int(r * 2)

    padded = QPixmap(sw + 2 * margin, sh + 2 * margin)
    p = QPainter(padded)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.drawPixmap(padded.rect(), source)
    p.drawPixmap(QRectF(margin, margin, sw, sh), source, QRectF(source.rect()))
    p.end()

    scene = QGraphicsScene()
    item = QGraphicsPixmapItem(padded)
    effect = QGraphicsBlurEffect()
    effect.setBlurRadius(r)
    effect.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)
    item.setGraphicsEffect(effect)
    scene.addItem(item)
    scene.setSceneRect(QRectF(padded.rect()))

    out = QImage(padded.size(), QImage.Format.Format_ARGB32_Premultiplied)
    out.fill(Qt.GlobalColor.black)
    p = QPainter(out)
    scene.render(p, QRectF(out.rect()), QRectF(padded.rect()))
    p.end()

    cropped = QPixmap.fromImage(out.copy(margin, margin, sw, sh))
    return cropped.scaled(
        source.size(),
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def cover_scaled(source: QPixmap, size: QSize, dpr: float) -> QPixmap:
    """Scale ``source`` to cover ``size`` (logical px), cropping the overflow."""
    if source.isNull() or size.isEmpty():
        return QPixmap()
    tw = max(1, round(size.width() * dpr))
    th = max(1, round(size.height() * dpr))
    scaled = source.scaled(
        tw, th,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = (scaled.width() - tw) // 2
    y = (scaled.height() - th) // 2
    out = scaled.copy(x, y, tw, th)
    out.setDevicePixelRatio(dpr)
    return out


def make_avatar(
    diameter: int, initials: str, accent_hex: str = "#0067C0", dpr: float = 1.0
) -> QPixmap:
    """Generate a circular account picture with initials."""
    pixels = max(1, round(diameter * dpr))
    pix = QPixmap(pixels, pixels)
    pix.fill(Qt.GlobalColor.transparent)
    pix.setDevicePixelRatio(dpr)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    rect = QRectF(0, 0, diameter, diameter)
    clip = QPainterPath()
    clip.addEllipse(rect)
    painter.setClipPath(clip)

    accent = Palette.accent(accent_hex)
    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, Palette.accent_light(accent_hex))
    grad.setColorAt(1.0, accent.darker(160))
    painter.fillRect(rect, grad)

    sheen = QRadialGradient(diameter * 0.3, diameter * 0.15, diameter * 0.85)
    sheen.setColorAt(0.0, QColor(255, 255, 255, 70))
    sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.fillRect(rect, sheen)

    painter.setPen(Palette.TEXT)
    painter.setFont(font(round(diameter * 0.36), QFont.Weight.DemiBold))
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)

    painter.setClipping(False)
    ring = max(1.0, diameter * 0.012)
    painter.setPen(QPen(QColor(255, 255, 255, 60), ring))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(rect.adjusted(ring / 2, ring / 2, -ring / 2, -ring / 2))

    painter.end()
    return pix
