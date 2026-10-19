"""Windows-11-style password box: reveal button and submit arrow inside it.

This widget never reads, stores, or compares against real Windows
credentials. It only hands the text typed into this in-app field to the
calling screen, which runs its own *simulated* check and then clears it.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QAbstractAnimation, QEvent, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QToolButton, QWidget

from ..theme import GLYPH_FALLBACK, Glyph, Scale, font, icon_font

_BUTTON_STYLE = """
QToolButton {{
    color: white; background: {bg}; border: none; border-radius: {r}px;
}}
QToolButton:hover {{ background: rgba(255,255,255,0.10); }}
QToolButton:pressed {{ background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.7); }}
QToolButton:checked {{ background: rgba(255,255,255,0.12); }}
QToolButton:focus {{ border: 1px solid rgba(255,255,255,0.8); }}
"""


class PasswordField(QFrame):
    """Rounded translucent box with an accent underline while focused."""

    submitted = Signal()

    def __init__(self, px: Scale, accent: QColor, parent: QWidget | None = None):
        super().__init__(parent)
        self._px = px
        self._accent = accent
        self._focused = False
        self._hovered = False
        self._shake_anim: QVariantAnimation | None = None
        self._icons = icon_font(px(13))
        self.setFixedSize(px(296), px(36))
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

        self.edit = QLineEdit(self)
        self.edit.setFrame(False)
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit.setPlaceholderText("Password")
        self.edit.setFont(font(px(15)))
        palette = self.edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(255, 255, 255, 170))
        palette.setColor(QPalette.ColorRole.Highlight, accent.darker(130))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.edit.setPalette(palette)
        self.edit.installEventFilter(self)
        self.edit.returnPressed.connect(self.submitted.emit)
        self.edit.textChanged.connect(self._on_text_changed)

        self.reveal_btn = self._make_button(Glyph.VIEW, "transparent")
        self.reveal_btn.setCheckable(True)
        self.reveal_btn.setToolTip("Show password")
        self.reveal_btn.toggled.connect(self._on_reveal)
        self.reveal_btn.hide()

        self.submit_btn = self._make_button(Glyph.FORWARD, "rgba(255,255,255,0.06)")
        self.submit_btn.setToolTip("Submit")
        self.submit_btn.clicked.connect(self.submitted.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(px(11), px(4), px(4), px(4))
        layout.setSpacing(px(2))
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.reveal_btn)
        layout.addWidget(self.submit_btn)

    def _make_button(self, glyph: str, background: str) -> QToolButton:
        px = self._px
        btn = QToolButton(self)
        btn.setFont(self._icons or font(px(15)))
        btn.setText(self._glyph(glyph))
        btn.setFixedSize(px(28), px(28))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        btn.setStyleSheet(_BUTTON_STYLE.format(bg=background, r=px(4)))
        return btn

    def _glyph(self, glyph: str) -> str:
        return glyph if self._icons else GLYPH_FALLBACK.get(glyph, glyph)

    # ---- state -------------------------------------------------------

    def _on_text_changed(self, text: str) -> None:
        self.reveal_btn.setVisible(bool(text))
        if not text:
            self.reveal_btn.setChecked(False)

    def _on_reveal(self, checked: bool) -> None:
        self.edit.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.reveal_btn.setText(self._glyph(Glyph.HIDE if checked else Glyph.VIEW))
        self.reveal_btn.setToolTip("Hide password" if checked else "Show password")

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 (Qt override)
        if obj is self.edit and event.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            self._focused = event.type() == QEvent.Type.FocusIn
            self.update()
        return super().eventFilter(obj, event)

    def enterEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    # ---- public API ----------------------------------------------------

    def text(self) -> str:
        return self.edit.text()

    def reset(self) -> None:
        self.edit.clear()
        self.reveal_btn.setChecked(False)

    def focus(self) -> None:
        self.edit.setFocus(Qt.FocusReason.OtherFocusReason)

    def shake(self) -> None:
        """Brief horizontal shake, used to reject input."""
        if self._shake_anim is not None:
            return
        origin = self.pos()
        amplitude = self._px(10)
        anim = QVariantAnimation(self)
        anim.setDuration(420)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)

        def step(value: float) -> None:
            offset = amplitude * math.sin(value * math.pi * 6) * (1 - value)
            self.move(origin.x() + round(offset), origin.y())

        def done() -> None:
            self.move(origin)
            self._shake_anim = None

        anim.valueChanged.connect(step)
        anim.finished.connect(done)
        self._shake_anim = anim
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    # ---- painting --------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = self._px(4)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        if self._focused:
            background = QColor(24, 24, 24, 210)
        elif self._hovered:
            background = QColor(70, 70, 70, 150)
        else:
            background = QColor(50, 50, 50, 140)
        painter.fillPath(path, background)
        painter.setPen(QPen(QColor(255, 255, 255, 70 if self._focused else 40), 1))
        painter.drawPath(path)

        painter.setClipPath(path)
        if self._focused:
            line = max(2, self._px(2))
            painter.fillRect(
                QRectF(rect.left(), rect.bottom() - line + 0.5, rect.width(), line),
                self._accent,
            )
        else:
            painter.fillRect(
                QRectF(rect.left(), rect.bottom() - 0.5, rect.width(), 1),
                QColor(255, 255, 255, 110),
            )
        painter.end()
