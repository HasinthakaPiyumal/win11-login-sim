"""Fluent-inspired colours, fonts and stylesheet.

Values approximate the Windows 11 sign-in look (Segoe UI typography, acrylic
darkening, rounded controls, the accent-coloured arrow button). All assets are
drawn by us; nothing is copied from Windows.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QFontDatabase


# Windows 11 uses "Segoe UI Variable" / "Segoe UI". We request them by name and
# gracefully fall back to whatever sans-serif the platform provides.
_PREFERRED_FAMILIES = (
    "Segoe UI Variable Display",
    "Segoe UI Variable",
    "Segoe UI",
    "Selawik",
)


def ui_font_family() -> str:
    """Return the best available Fluent-like font family."""
    available = set(QFontDatabase.families())
    for family in _PREFERRED_FAMILIES:
        if family in available:
            return family
    return QFont().defaultFamily()


def font(size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    """Convenience constructor for a themed font at the given pixel size."""
    f = QFont(ui_font_family())
    f.setPixelSize(size)
    f.setWeight(weight)
    return f


class Palette:
    """Named colours used across the screens."""

    TEXT = QColor(255, 255, 255)
    TEXT_DIM = QColor(255, 255, 255, 190)
    TEXT_FAINT = QColor(255, 255, 255, 140)

    # Acrylic-like darkening laid over the wallpaper on the login screen.
    LOGIN_SCRIM = QColor(0, 0, 0, 150)

    # Password field (semi-transparent dark pill with a light border).
    FIELD_BG = "rgba(60, 60, 60, 0.55)"
    FIELD_BORDER = "rgba(255, 255, 255, 0.35)"
    FIELD_BORDER_FOCUS = "rgba(255, 255, 255, 0.85)"

    @staticmethod
    def accent(hex_value: str) -> QColor:
        c = QColor(hex_value)
        return c if c.isValid() else QColor("#0067C0")
