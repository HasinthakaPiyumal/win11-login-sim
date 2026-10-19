"""Windows-11-style sign-in: avatar, name, password box, then "Welcome".

IMPORTANT: This screen simulates authentication locally only. It never reads
real Windows credentials, never calls any Windows authentication API, and
never transmits anything anywhere. ``Config.check_password`` decides whether
the demonstration input is accepted (by default: any non-empty text), and the
typed text is cleared immediately after that check.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..assets import make_avatar
from ..config import Config
from ..theme import Glyph, Palette, Scale, font
from ..widgets.password_field import PasswordField
from ..widgets.spinner import Spinner
from ..widgets.status_icons import StatusIcons
from .base import BackgroundScreen

_SIGN_IN_DELAY_MS = 1800


def _white_label(text: str, size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QLabel:
    label = QLabel(text)
    label.setFont(font(size, weight))
    label.setStyleSheet("color: white;")
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    return label


class LoginScreen(BackgroundScreen):
    """Second screen: the sign-in card over the blurred wallpaper."""

    sign_in_succeeded = Signal()

    def __init__(self, background: QPixmap, cfg: Config, px: Scale, parent: QWidget | None = None):
        super().__init__(background, px, parent)
        self.cfg = cfg
        self._busy = False

        root = QVBoxLayout(self)
        root.setContentsMargins(px(24), 0, px(24), px(20))
        root.setSpacing(0)
        root.addStretch(5)

        self.card = QWidget(self)
        card = QVBoxLayout(self.card)
        card.setContentsMargins(0, 0, 0, 0)
        card.setSpacing(0)

        diameter = px(192)
        screen = QGuiApplication.primaryScreen()
        dpr = screen.devicePixelRatio() if screen else 1.0
        avatar = QLabel(self.card)
        avatar.setFixedSize(diameter, diameter)
        avatar.setPixmap(make_avatar(diameter, cfg.initials, cfg.accent_hex, dpr))
        shadow = QGraphicsDropShadowEffect(avatar)
        shadow.setBlurRadius(px(40))
        shadow.setOffset(0, px(6))
        shadow.setColor(QColor(0, 0, 0, 110))
        avatar.setGraphicsEffect(shadow)
        card.addWidget(avatar, 0, Qt.AlignmentFlag.AlignHCenter)
        card.addSpacing(px(20))

        card.addWidget(_white_label(cfg.display_name, px(28), QFont.Weight.DemiBold))
        card.addSpacing(px(26))

        # Stage: page 0 = password entry, page 1 = spinner + "Welcome".
        self.stage = QStackedWidget(self.card)
        self.stage.setFixedSize(px(340), px(96))

        entry = QWidget()
        entry_layout = QVBoxLayout(entry)
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.setSpacing(px(14))
        self.password = PasswordField(px, Palette.accent_light(cfg.accent_hex), entry)
        self.password.submitted.connect(self._on_submit)
        entry_layout.addWidget(self.password, 0, Qt.AlignmentFlag.AlignHCenter)
        self.error_label = _white_label("", px(14))
        self.error_label.setWordWrap(True)
        entry_layout.addWidget(self.error_label)
        entry_layout.addStretch(1)
        self.password.edit.textEdited.connect(lambda _text: self.error_label.clear())

        busy = QWidget()
        busy_layout = QVBoxLayout(busy)
        busy_layout.setContentsMargins(0, 0, 0, 0)
        busy_layout.setSpacing(px(14))
        self.spinner = Spinner(px(36), busy)
        busy_layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignHCenter)
        busy_layout.addWidget(_white_label("Welcome", px(20)))
        busy_layout.addStretch(1)

        self.stage.addWidget(entry)
        self.stage.addWidget(busy)
        card.addWidget(self.stage, 0, Qt.AlignmentFlag.AlignHCenter)

        root.addWidget(self.card, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(6)

        status = QHBoxLayout()
        status.addStretch(1)
        status.addWidget(
            StatusIcons((Glyph.WIFI, Glyph.ACCESSIBILITY, Glyph.POWER), px, self)
        )
        root.addLayout(status)

        self._fade_effect = QGraphicsOpacityEffect(self.card)
        self._fade_effect.setEnabled(False)
        self.card.setGraphicsEffect(self._fade_effect)
        self._fade_anim = QPropertyAnimation(self._fade_effect, b"opacity", self)
        self._fade_anim.setDuration(450)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        # Drop the offscreen effect once visible so typing stays snappy.
        self._fade_anim.finished.connect(lambda: self._fade_effect.setEnabled(False))

    def paint_overlay(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))

    def on_shown(self, typed: str = "") -> None:
        """Called every time this screen becomes visible."""
        self.reset_busy()
        self.error_label.clear()
        self.password.reset()
        if typed:
            self.password.edit.setText(typed)
        self.password.focus()
        self._fade_effect.setEnabled(True)
        self._fade_anim.start()

    def reset_busy(self) -> None:
        self._busy = False
        self.spinner.stop()
        self.stage.setCurrentIndex(0)

    def _on_submit(self) -> None:
        if self._busy:
            return
        text = self.password.text()
        if not text.strip():
            self.password.shake()
            return
        accepted = self.cfg.check_password(text)
        # Discard the typed text right away; nothing is kept.
        self.password.reset()
        self._busy = True
        self.error_label.clear()
        self.stage.setCurrentIndex(1)
        self.spinner.start()
        QTimer.singleShot(_SIGN_IN_DELAY_MS, lambda: self._finish_submit(accepted))

    def _finish_submit(self, accepted: bool) -> None:
        if accepted:
            self.sign_in_succeeded.emit()
            return
        self.reset_busy()
        self.error_label.setText("The password is incorrect. Try again.")
        self.password.focus()
        self.password.shake()
