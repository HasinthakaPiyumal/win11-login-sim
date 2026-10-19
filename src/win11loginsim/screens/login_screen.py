"""Windows-11-style sign-in card: avatar, name, password field, arrow button.

IMPORTANT: This screen simulates authentication locally only. It never reads
real Windows credentials, never calls any Windows authentication API, and
never transmits anything anywhere. ``Config.check_password`` decides whether
the demonstration input is accepted (by default: any non-empty text).
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..assets import make_avatar
from ..config import Config
from ..theme import Palette, font
from ..widgets.password_field import PasswordField
from ..widgets.spinner import Spinner


class LoginScreen(QWidget):
    """Second screen: the actual sign-in card over the wallpaper."""

    sign_in_succeeded = Signal()

    def __init__(self, wallpaper, cfg: Config, parent: QWidget | None = None):
        super().__init__(parent)
        self._wallpaper = wallpaper
        self.cfg = cfg
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(2)

        card = QVBoxLayout()
        card.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card.setSpacing(10)

        self.avatar_label = QLabel(self)
        self.avatar_label.setFixedSize(96, 96)
        self.avatar_label.setPixmap(make_avatar(96, cfg.initials, cfg.accent_hex))
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.addWidget(self.avatar_label, 0, Qt.AlignmentFlag.AlignHCenter)

        name_label = QLabel(cfg.display_name, self)
        name_label.setFont(font(22))
        name_label.setStyleSheet("color: white; background: transparent;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card.addWidget(name_label)
        card.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.password = PasswordField("Password", self)
        self.password.setFixedWidth(260)
        self.password.submitted.connect(self._on_submit)
        row.addWidget(self.password)

        self.sign_in_btn = QPushButton("→", self)  # right arrow
        self.sign_in_btn.setFixedSize(40, 40)
        self.sign_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sign_in_btn.setFont(font(16))
        self.sign_in_btn.clicked.connect(self._on_submit)
        row.addWidget(self.sign_in_btn)
        self._style_button(cfg.accent_hex)

        row_widget = QWidget(self)
        row_widget.setLayout(row)
        card.addWidget(row_widget, 0, Qt.AlignmentFlag.AlignHCenter)

        self.spinner = Spinner(26, self)
        card.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignHCenter)

        self.error_label = QLabel("", self)
        self.error_label.setFont(font(13))
        self.error_label.setStyleSheet("color: #ffb4b4; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.error_label.setFixedHeight(20)
        card.addWidget(self.error_label)

        card_widget = QWidget(self)
        card_widget.setLayout(card)
        outer.addWidget(card_widget, 0, Qt.AlignmentFlag.AlignHCenter)

        outer.addStretch(3)
        self.setLayout(outer)

        self._fade_effect = QGraphicsOpacityEffect(card_widget)
        card_widget.setGraphicsEffect(self._fade_effect)
        self._fade_anim = QPropertyAnimation(self._fade_effect, b"opacity", self)
        self._fade_anim.setDuration(350)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _style_button(self, accent_hex: str) -> None:
        accent = Palette.accent(accent_hex)
        self.sign_in_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(255,255,255,0.12);
                color: white;
                border: 1px solid rgba(255,255,255,0.35);
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: rgb({accent.red()},{accent.green()},{accent.blue()});
                border: 1px solid rgb({accent.red()},{accent.green()},{accent.blue()});
            }}
            QPushButton:disabled {{
                background: rgba(255,255,255,0.08);
                color: rgba(255,255,255,0.4);
            }}
            """
        )

    def on_shown(self) -> None:
        """Called every time this screen becomes visible."""
        self.error_label.setText("")
        self.password.clear()
        self.password.set_focus()
        self._fade_anim.start()

    def _on_submit(self) -> None:
        text = self.password.text()
        if not text.strip():
            self.error_label.setText("Enter anything to continue (demo mode)")
            return
        self._set_busy(True)
        # Brief, clearly-simulated "signing in" delay before the check runs.
        QTimer.singleShot(900, lambda: self._finish_submit(text))

    def _finish_submit(self, text: str) -> None:
        if self.cfg.check_password(text):
            self.sign_in_succeeded.emit()
        else:
            self._set_busy(False)
            self.error_label.setText("That's not quite right. Try again (any text works).")
            self.password.clear()
            self.password.set_focus()

    def _set_busy(self, busy: bool) -> None:
        self.password.set_enabled_all(not busy)
        self.sign_in_btn.setEnabled(not busy)
        if busy:
            self.error_label.setText("")
            self.spinner.start()
        else:
            self.spinner.stop()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        if not self._wallpaper.isNull():
            scaled = self._wallpaper.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
        painter.fillRect(self.rect(), Palette.LOGIN_SCRIM)
        painter.end()
        super().paintEvent(event)
