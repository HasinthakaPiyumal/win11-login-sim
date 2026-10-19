"""Configuration loading and saving.

The configuration lives as JSON in the per-user application data directory.
It is created with safe defaults on first run. All values are purely cosmetic
or behavioural for the *simulation* — none of them affect the operating system.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict

from .utils.paths import config_path

log = logging.getLogger(__name__)


@dataclass
class Config:
    """User-facing settings for the simulation.

    Attributes:
        display_name: Name shown under the avatar.
        avatar_initials: Two letters drawn on the generated avatar. If empty,
            initials are derived from ``display_name``.
        demo_mode: How the fake "password" is validated.
            - ``"any"``   : accept any non-empty input (default).
            - ``"fixed"`` : accept only ``demo_password``.
        demo_password: The accepted value when ``demo_mode == "fixed"``.
        show_clock: Show the lock-screen clock/date before the login card.
        stay_on_top: Keep the window above others (typical for a prank). The
            safety exit still always works regardless of this value.
        allow_escape_exit: Allow the Escape key to quit (handy during testing).
        countdown_seconds: Optional countdown on the surprise screen. 0 hides
            it. The countdown is purely decorative and never forces a quit.
        surprise_title: First line on the surprise screen.
        surprise_subtitle: Second line on the surprise screen.
        accent_hex: Fluent accent colour used for the sign-in button and ring.
    """

    display_name: str = "User"
    avatar_initials: str = ""
    demo_mode: str = "any"
    demo_password: str = "surprise"
    show_clock: bool = True
    stay_on_top: bool = True
    allow_escape_exit: bool = True
    countdown_seconds: int = 0
    surprise_title: str = "You have a surprise!"
    surprise_subtitle: str = "I will give you access later."
    accent_hex: str = "#0067C0"

    # ---- helpers -------------------------------------------------------

    @property
    def initials(self) -> str:
        """Return the initials to paint on the avatar."""
        if self.avatar_initials.strip():
            return self.avatar_initials.strip()[:2].upper()
        parts = [p for p in self.display_name.split() if p]
        if not parts:
            return "U"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def check_password(self, text: str) -> bool:
        """Validate simulated input. Never touches real authentication."""
        if self.demo_mode == "fixed":
            return text == self.demo_password
        # "any" (default): accept any non-empty demonstration input.
        return bool(text.strip())


def _coerce(data: Dict[str, Any]) -> Config:
    """Build a Config from a dict, ignoring unknown keys and bad types."""
    valid = {f.name: f.type for f in fields(Config) if f.init}
    kwargs: Dict[str, Any] = {}
    defaults = Config()
    for name in valid:
        if name not in data:
            continue
        value = data[name]
        default = getattr(defaults, name)
        # Keep the default if the stored type is incompatible.
        if isinstance(default, bool):
            kwargs[name] = bool(value)
        elif isinstance(default, int) and not isinstance(value, bool):
            try:
                kwargs[name] = int(value)
            except (TypeError, ValueError):
                continue
        elif isinstance(default, str):
            kwargs[name] = str(value)
        else:
            kwargs[name] = value
    return Config(**kwargs)


def load_config() -> Config:
    """Load configuration, creating defaults on first run.

    Any read/parse error is logged and recovered from by falling back to
    defaults, so a corrupt file never prevents the app from starting.
    """
    path = config_path()
    if not path.exists():
        cfg = Config()
        save_config(cfg)
        log.info("Created default config at %s", path)
        return cfg
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("config root is not an object")
        return _coerce(data)
    except Exception:  # noqa: BLE001 - never let config break startup
        log.exception("Failed to read config %s; using defaults", path)
        return Config()


def save_config(cfg: Config) -> None:
    """Persist configuration as pretty-printed JSON."""
    path = config_path()
    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(cfg), fh, indent=2, ensure_ascii=False)
    except OSError:
        log.exception("Failed to write config %s", path)
