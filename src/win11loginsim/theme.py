"""Fluent-inspired colours, fonts, icon glyphs and sizing helpers.

Values approximate the Windows 11 sign-in look (Segoe UI Variable typography,
acrylic-style blur, rounded controls, Segoe Fluent Icons). All artwork is drawn
by this project; nothing is copied from Windows.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional, Tuple

from PySide6.QtGui import QColor, QFont, QFontDatabase

_TEXT_FAMILIES = (
    "Segoe UI Variable Display",
    "Segoe UI Variable",
    "Segoe UI",
    "Selawik",
)
_ICON_FAMILIES = ("Segoe Fluent Icons", "Segoe MDL2 Assets")
_EMOJI_FAMILIES = ("Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji")


@lru_cache(maxsize=None)
def _first_available(candidates: Tuple[str, ...]) -> Optional[str]:
    available = set(QFontDatabase.families())
    for family in candidates:
        if family in available:
            return family
    return None


def ui_font_family() -> str:
    """Return the best available Fluent-like text font family."""
    return _first_available(_TEXT_FAMILIES) or QFont().defaultFamily()


def font(size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    """Themed text font at the given pixel size."""
    f = QFont(ui_font_family())
    f.setPixelSize(max(1, size))
    f.setWeight(weight)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return f


def icon_font(size: int) -> Optional[QFont]:
    """Segoe Fluent Icons (Windows 11) or MDL2 (Windows 10), else None."""
    family = _first_available(_ICON_FAMILIES)
    if family is None:
        return None
    f = QFont(family)
    f.setPixelSize(max(1, size))
    return f


def emoji_font(size: int) -> QFont:
    """Colour emoji font, falling back to the text font."""
    f = QFont(_first_available(_EMOJI_FAMILIES) or ui_font_family())
    f.setPixelSize(max(1, size))
    return f


class Glyph:
    """Segoe Fluent Icons / MDL2 code points used in the UI."""

    FORWARD = ""
    VIEW = ""
    HIDE = ""
    WIFI = ""
    BATTERY = ""
    ACCESSIBILITY = ""
    POWER = ""


# Plain-text stand-ins for when no Fluent icon font exists (e.g. dev on Linux).
GLYPH_FALLBACK = {
    Glyph.FORWARD: "→",
    Glyph.VIEW: "◉",
    Glyph.HIDE: "○",
}


def ui_scale(logical_height: int) -> float:
    """Size multiplier for the current screen.

    Windows lays out its sign-in UI in effective (DPI-independent) pixels, so
    the scale stays at 1.0 for typical displays and only shrinks for very
    short screens or grows a little on very tall ones.
    """
    if logical_height < 800:
        return max(0.7, logical_height / 800)
    if logical_height > 1400:
        return min(1.35, logical_height / 1400)
    return 1.0


class Scale:
    """Callable that converts design pixels to scaled pixels: ``px(16)``."""

    def __init__(self, factor: float):
        self.factor = factor

    def __call__(self, value: float) -> int:
        return max(1, round(value * self.factor))


class Palette:
    """Named colours used across the screens."""

    TEXT = QColor(255, 255, 255)

    @staticmethod
    def accent(hex_value: str) -> QColor:
        c = QColor(hex_value)
        return c if c.isValid() else QColor("#0067C0")

    @staticmethod
    def accent_light(hex_value: str) -> QColor:
        """Light accent variant, as Windows uses on dark surfaces."""
        c = Palette.accent(hex_value)
        hue = c.hsvHueF()
        if hue < 0:
            hue = 0.57
        return QColor.fromHsvF(hue, min(1.0, c.hsvSaturationF() * 0.7), 1.0)
