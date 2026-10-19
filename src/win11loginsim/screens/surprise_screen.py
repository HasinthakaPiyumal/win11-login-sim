"""Surprise screen shown after the simulated sign-in succeeds.

Fully custom-painted: drifting bokeh lights, twinkling sparkles, a bobbing
gift with a soft glow, and the configured message, all fading in with a
staggered entrance. Closing is always possible via the shortcuts documented
in README.md / RECOVERY.md (enforced in ``app.py``).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6.QtCore import QElapsedTimer, QPointF, QRect, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from ..config import Config
from ..theme import Palette, Scale, emoji_font, font
from .base import BackgroundScreen

_CENTER_WRAP = Qt.AlignmentFlag.AlignHCenter.value | Qt.TextFlag.TextWordWrap.value
_GIFT = "\U0001F381"


@dataclass
class _Light:
    x: float       # 0..1 of width
    y: float       # 0..1 of height
    radius: float  # logical px
    speed: float   # fraction of height per second
    sway: float    # logical px
    phase: float
    alpha: int
    tinted: bool


@dataclass
class _Sparkle:
    angle: float
    distance: float  # 0..1 of the sparkle ellipse
    size: float
    speed: float
    phase: float


def _ease_out(progress: float) -> float:
    progress = min(1.0, max(0.0, progress))
    return 1 - (1 - progress) ** 3


def _sparkle_path(cx: float, cy: float, r: float) -> QPainterPath:
    path = QPainterPath(QPointF(cx, cy - r))
    path.quadTo(cx, cy, cx + r, cy)
    path.quadTo(cx, cy, cx, cy + r)
    path.quadTo(cx, cy, cx - r, cy)
    path.quadTo(cx, cy, cx, cy - r)
    return path


class SurpriseScreen(BackgroundScreen):
    """Final screen: the reveal message plus optional decorative countdown."""

    def __init__(self, background: QPixmap, cfg: Config, px: Scale, parent: QWidget | None = None):
        super().__init__(background, px, parent)
        self.cfg = cfg
        self._accent = Palette.accent_light(cfg.accent_hex)
        self._clock = QElapsedTimer()
        self._frame_timer = QTimer(self)
        self._frame_timer.setInterval(16)
        self._frame_timer.timeout.connect(self.update)
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick)
        self._remaining = 0
        self._countdown_text = ""

        rng = random.Random(11)
        self._lights = [
            _Light(
                x=rng.random(), y=rng.random(),
                radius=px(rng.uniform(6, 70)),
                speed=rng.uniform(0.008, 0.03),
                sway=px(rng.uniform(10, 40)),
                phase=rng.uniform(0, math.tau),
                alpha=rng.randint(14, 46),
                tinted=rng.random() < 0.55,
            )
            for _ in range(34)
        ]
        self._sparkles = [
            _Sparkle(
                angle=rng.uniform(0, math.tau),
                distance=rng.uniform(0.45, 1.0),
                size=px(rng.uniform(5, 12)),
                speed=rng.uniform(1.2, 2.6),
                phase=rng.uniform(0, math.tau),
            )
            for _ in range(14)
        ]

    # ---- lifecycle -------------------------------------------------------

    def on_shown(self) -> None:
        """(Re)start the entrance animation and optional countdown."""
        self._clock.start()
        self._frame_timer.start()
        self._remaining = max(0, int(self.cfg.countdown_seconds))
        self._countdown_text = self._countdown_label()
        if self._remaining > 0:
            self._countdown_timer.start()

    def hideEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._frame_timer.stop()
        self._countdown_timer.stop()
        super().hideEvent(event)

    def _tick(self) -> None:
        self._remaining -= 1
        if self._remaining <= 0:
            self._countdown_timer.stop()
        self._countdown_text = self._countdown_label()

    def _countdown_label(self) -> str:
        if self.cfg.countdown_seconds <= 0:
            return ""
        if self._remaining > 0:
            return f"Access opens in {self._remaining}s"
        return "Whenever you're ready ✨"

    # ---- painting --------------------------------------------------------

    def paint_overlay(self, p: QPainter) -> None:
        px = self.px
        w, h = self.width(), self.height()
        t = self._clock.elapsed() / 1000.0 if self._clock.isValid() else 0.0

        scrim = QLinearGradient(0, 0, 0, h)
        scrim.setColorAt(0.0, QColor(0, 0, 0, 60))
        scrim.setColorAt(1.0, QColor(0, 0, 0, 150))
        p.fillRect(self.rect(), scrim)

        self._paint_lights(p, t, w, h)

        title_font = font(px(54), QFont.Weight.DemiBold)
        sub_font = font(px(22))
        small_font = font(px(16))
        max_w = min(w - px(80), px(1100))
        text_box = QRect(0, 0, max_w, 10_000)
        title = self.cfg.surprise_title
        subtitle = self.cfg.surprise_subtitle
        title_h = QFontMetrics(title_font).boundingRect(text_box, _CENTER_WRAP, title).height()
        sub_h = QFontMetrics(sub_font).boundingRect(text_box, _CENTER_WRAP, subtitle).height()
        small_h = QFontMetrics(small_font).height() if self._countdown_text else 0

        gift_box = px(150)
        total = gift_box + px(18) + title_h + px(14) + sub_h
        if small_h:
            total += px(26) + small_h
        y = (h - total) / 2 - px(24)
        left = (w - max_w) / 2
        rise = px(30)

        # Gift with glow, gentle bob and wobble.
        e = _ease_out(t / 0.9)
        gift_center = QPointF(w / 2, y + gift_box / 2 + (1 - e) * rise)
        glow = QRadialGradient(gift_center, px(190))
        glow.setColorAt(0.0, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), int(120 * e)))
        glow.setColorAt(1.0, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 0))
        p.fillRect(self.rect(), glow)
        self._paint_sparkles(p, t, gift_center, _ease_out((t - 0.3) / 0.9))

        p.save()
        p.setOpacity(e)
        p.translate(gift_center + QPointF(0, math.sin(t * 1.8) * px(7)))
        p.rotate(math.sin(t * 1.3) * 4)
        p.setFont(emoji_font(px(104)))
        p.setPen(QColor(255, 255, 255))
        p.drawText(QRectF(-gift_box, -gift_box / 2, gift_box * 2, gift_box), Qt.AlignmentFlag.AlignCenter, _GIFT)
        p.restore()
        y += gift_box + px(18)

        # Title with a soft shadow and accent-tinted gradient.
        e = _ease_out((t - 0.12) / 0.9)
        rect = QRectF(left, y + (1 - e) * rise, max_w, title_h)
        p.setOpacity(e)
        p.setFont(title_font)
        p.setPen(QColor(0, 0, 0, 80))
        p.drawText(rect.translated(0, px(2)), _CENTER_WRAP, title)
        half = min(max_w, QFontMetrics(title_font).horizontalAdvance(title)) / 2
        shine = QLinearGradient(w / 2 - half, 0, w / 2 + half, 0)
        shine.setColorAt(0.0, QColor(255, 255, 255))
        shine.setColorAt(0.5, self._accent)
        shine.setColorAt(1.0, QColor(255, 255, 255))
        p.setPen(QPen(shine, 1))
        p.drawText(rect, _CENTER_WRAP, title)
        y += title_h + px(14)

        e = _ease_out((t - 0.24) / 0.9)
        p.setOpacity(e)
        p.setFont(sub_font)
        p.setPen(QColor(255, 255, 255, 215))
        p.drawText(QRectF(left, y + (1 - e) * rise, max_w, sub_h), _CENTER_WRAP, subtitle)
        y += sub_h

        if small_h:
            y += px(26)
            e = _ease_out((t - 0.4) / 0.9)
            p.setOpacity(e)
            p.setFont(small_font)
            p.setPen(QColor(255, 255, 255, 170))
            p.drawText(QRectF(left, y + (1 - e) * rise, max_w, small_h), _CENTER_WRAP, self._countdown_text)
        p.setOpacity(1.0)

    def _paint_lights(self, p: QPainter, t: float, w: int, h: int) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        for light in self._lights:
            y = ((light.y - light.speed * t) % 1.2 - 0.1) * h
            x = light.x * w + math.sin(t * 0.4 + light.phase) * light.sway
            base = self._accent if light.tinted else QColor(255, 255, 255)
            grad = QRadialGradient(QPointF(x, y), light.radius)
            grad.setColorAt(0.0, QColor(base.red(), base.green(), base.blue(), light.alpha))
            grad.setColorAt(0.7, QColor(base.red(), base.green(), base.blue(), light.alpha // 3))
            grad.setColorAt(1.0, QColor(base.red(), base.green(), base.blue(), 0))
            p.setBrush(grad)
            p.drawEllipse(QPointF(x, y), light.radius, light.radius)

    def _paint_sparkles(self, p: QPainter, t: float, center: QPointF, visibility: float) -> None:
        if visibility <= 0:
            return
        rx, ry = self.px(380), self.px(200)
        p.setPen(Qt.PenStyle.NoPen)
        for s in self._sparkles:
            twinkle = max(0.0, math.sin(t * s.speed + s.phase)) ** 2
            if twinkle < 0.02:
                continue
            x = center.x() + math.cos(s.angle) * rx * s.distance
            y = center.y() + math.sin(s.angle) * ry * s.distance + self.px(60)
            p.setBrush(QColor(255, 255, 255, int(230 * twinkle * visibility)))
            p.drawPath(_sparkle_path(x, y, s.size * (0.6 + 0.4 * twinkle)))
