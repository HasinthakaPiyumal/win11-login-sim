"""Main window: orchestrates the lock -> login -> surprise screen sequence.

Safety design (do not weaken these without re-reading README.md / RECOVERY.md):

* ``Ctrl+Shift+Q`` always quits the application immediately, regardless of
  config, current screen, or any error state. It is wired at the top-level
  window and is never disabled.
* ``Escape`` also quits when ``cfg.allow_escape_exit`` is true (default),
  intended for development/testing convenience.
* The window never installs any keyboard hook, driver, or system-wide input
  filter. It only reacts to key events Qt delivers to *this* window, exactly
  like any other application. Ctrl+Alt+Del and other Windows security
  shortcuts are never intercepted and are not reachable by a normal
  application at all.
* Closing the window (Alt+F4, taskbar, task manager) always works. We do not
  override ``closeEvent`` to block it.
"""

from __future__ import annotations

import logging
import sys

from PySide6.QtCore import QAbstractAnimation, QEasingCurve, QPoint, QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QGuiApplication, QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .assets import blur_pixmap, make_wallpaper
from .config import Config, load_config
from .theme import Scale, ui_scale
from .screens.lock_screen import LockScreen
from .screens.login_screen import LoginScreen
from .screens.surprise_screen import SurpriseScreen

log = logging.getLogger(__name__)


class MainWindow(QWidget):
    """Top-level full-screen window hosting the three simulation screens."""

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("Sign-in Simulation (not a real Windows sign-in screen)")

        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        dpr = screen.devicePixelRatio()
        px = Scale(ui_scale(geometry.height()))
        wallpaper = make_wallpaper(
            round(geometry.width() * dpr), round(geometry.height() * dpr), cfg.accent_hex
        )
        # Acrylic-style backdrop for the sign-in and surprise screens.
        backdrop = blur_pixmap(wallpaper, max(wallpaper.width(), wallpaper.height()) / 30)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self._transitioning = False

        self.stack = QStackedWidget(self)
        self.lock_screen = LockScreen(wallpaper, cfg, px, self.stack)
        self.login_screen = LoginScreen(backdrop, cfg, px, self.stack)
        self.surprise_screen = SurpriseScreen(backdrop, cfg, px, self.stack)

        for w in (self.lock_screen, self.login_screen, self.surprise_screen):
            self.stack.addWidget(w)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.stack)
        self.setLayout(root)
        self.lock_screen.advance_requested.connect(self._show_login)
        self.login_screen.sign_in_succeeded.connect(self._show_surprise)

        self._install_safety_shortcuts()

        if cfg.stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    # ---- safety -----------------------------------------------------

    def _install_safety_shortcuts(self) -> None:
        """Wire the guaranteed recovery shortcut plus optional Escape exit.

        Uses QShortcut (a normal, per-window Qt accelerator) -- not a global
        hook. It only fires while this window has focus, exactly like any
        other application's keyboard shortcuts.
        """
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        quit_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        quit_shortcut.activated.connect(self._safe_quit)
        self._quit_shortcut = quit_shortcut  # keep a reference alive

        if self.cfg.allow_escape_exit:
            esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
            esc_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            esc_shortcut.activated.connect(self._safe_quit)
            self._esc_shortcut = esc_shortcut

    def _safe_quit(self) -> None:
        log.info("Safety exit triggered; closing simulation.")
        QApplication.instance().quit()

    # ---- screen transitions ------------------------------------------

    def _snapshot_overlay(self, source: QWidget) -> QLabel:
        """Freeze ``source`` into a label above the stack for a transition."""
        overlay = QLabel(self)
        overlay.setPixmap(source.grab())
        overlay.setGeometry(self.rect())
        overlay.show()
        overlay.raise_()
        return overlay

    def _show_login(self, typed: str = "") -> None:
        """Slide the lock screen up to reveal the sign-in screen."""
        if self._transitioning or self.stack.currentWidget() is not self.lock_screen:
            return
        self._transitioning = True
        overlay = self._snapshot_overlay(self.lock_screen)
        self.stack.setCurrentWidget(self.login_screen)
        self.login_screen.on_shown(typed)

        anim = QPropertyAnimation(overlay, b"pos", self)
        anim.setDuration(500)
        anim.setStartValue(QPoint(0, 0))
        anim.setEndValue(QPoint(0, -self.height()))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(overlay.deleteLater)
        anim.finished.connect(lambda: setattr(self, "_transitioning", False))
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _show_surprise(self) -> None:
        """Cross-fade from the sign-in screen to the surprise screen."""
        overlay = self._snapshot_overlay(self.login_screen)
        effect = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(effect)
        self.stack.setCurrentWidget(self.surprise_screen)
        self.surprise_screen.on_shown()
        self.login_screen.reset_busy()

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(700)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(overlay.deleteLater)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


def run() -> int:
    """Application entry point. Returns the process exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Win11LoginSim")
    # Fusion renders our custom-styled controls identically on every machine.
    app.setStyle("Fusion")

    try:
        cfg = load_config()
    except Exception:  # noqa: BLE001 - never fail to start over bad config
        log.exception("Unexpected error loading config; using safe defaults.")
        cfg = Config()

    try:
        window = MainWindow(cfg)
    except Exception:
        log.exception("Fatal error constructing the UI.")
        return 1

    window.showFullScreen()
    window.lock_screen.setFocus()

    try:
        return app.exec()
    except Exception:  # noqa: BLE001 - last-resort safety net
        log.exception("Unhandled exception in event loop; exiting.")
        return 1
