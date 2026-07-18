from typing import Callable, Optional


class ThemeService:
    """Manages UI theme (light/dark)."""

    def __init__(self):
        self._dark_mode = False
        self._on_change: Optional[Callable] = None

    @property
    def is_dark(self) -> bool:
        return self._dark_mode

    def toggle(self) -> None:
        self._dark_mode = not self._dark_mode
        if self._on_change:
            self._on_change(self._dark_mode)

    def set_dark(self, dark: bool) -> None:
        self._dark_mode = dark
        if self._on_change:
            self._on_change(dark)

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback
