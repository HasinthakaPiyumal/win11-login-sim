"""Password-style input field with a show/hide toggle, Win11-pill style.

This widget never reads, stores, or compares against real Windows
credentials. It only reports back the raw text the user typed into this
in-app field so the calling screen can run its own *simulated* check.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QWidget

from ..theme import Palette, font


class PasswordField(QWidget):
    """A line edit with a Fluent-pill look and an eye-icon visibility toggle."""

    submitted = Signal()

    def __init__(self, placeholder: str = "Password", parent: QWidget | None = None):
        super().__init__(parent)
        self._reveal = False

        self.edit = QLineEdit(self)
        self.edit.setPlaceholderText(placeholder)
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit.setFont(font(15))
        self.edit.setFixedHeight(40)
        self.edit.returnPressed.connect(self.submitted.emit)
        self.edit.setStyleSheet(
            f"""
            QLineEdit {{
                background: {Palette.FIELD_BG};
                color: white;
                border: 1px solid {Palette.FIELD_BORDER};
                border-radius: 4px;
                padding: 0 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Palette.FIELD_BORDER_FOCUS};
            }}
            """
        )

        self.toggle_btn = QToolButton(self)
        self.toggle_btn.setText("\U0001F441")  # eye emoji, no asset needed
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setToolTip("Show/hide characters")
        self.toggle_btn.setStyleSheet(
            """
            QToolButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 15px;
                border-radius: 4px;
            }
            QToolButton:hover { background: rgba(255,255,255,0.12); }
            QToolButton:checked { background: rgba(255,255,255,0.20); }
            """
        )
        self.toggle_btn.toggled.connect(self._on_toggle)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.toggle_btn, 0)
        self.setLayout(layout)

        container_style = (
            f"background: {Palette.FIELD_BG}; border-radius: 4px;"
        )
        self.setStyleSheet(f"QWidget#pwContainer {{ {container_style} }}")
        self.setObjectName("pwContainer")
        # The edit already carries its own background; keep container clear.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def _on_toggle(self, checked: bool) -> None:
        self._reveal = checked
        self.edit.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.toggle_btn.setText("\U0001F576" if checked else "\U0001F441")

    def text(self) -> str:
        return self.edit.text()

    def clear(self) -> None:
        self.edit.clear()
        self.toggle_btn.setChecked(False)

    def set_focus(self) -> None:
        self.edit.setFocus(Qt.FocusReason.OtherFocusReason)

    def set_enabled_all(self, enabled: bool) -> None:
        self.edit.setEnabled(enabled)
        self.toggle_btn.setEnabled(enabled)
