"""Bottom-right system glyphs (network, battery, power...) as on Windows 11.

Decorative only: they show hover feedback but perform no system action.
Hidden automatically when no Fluent icon font is installed.
"""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QWidget

from ..theme import Scale, icon_font


class StatusIcons(QWidget):
    def __init__(self, glyphs: Iterable[str], px: Scale, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(px(4))

        icons = icon_font(px(16))
        if icons is None:
            self.hide()
            return

        style = (
            "QToolButton { color: white; background: transparent; border: none;"
            f" border-radius: {px(4)}px; }}"
            " QToolButton:hover { background: rgba(255,255,255,0.10); }"
            " QToolButton:pressed { background: rgba(255,255,255,0.05); }"
        )
        for glyph in glyphs:
            btn = QToolButton(self)
            btn.setText(glyph)
            btn.setFont(icons)
            btn.setFixedSize(px(40), px(40))
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setStyleSheet(style)
            layout.addWidget(btn)
