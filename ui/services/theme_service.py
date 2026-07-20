from typing import Callable, Optional


class ThemeService:
    def __init__(self):
        self._theme: str = "light"
        self._on_change: Optional[Callable] = None

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str) -> None:
        valid = {"light", "dark", "system", "high_contrast"}
        if value not in valid:
            value = "light"
        self._theme = value
        if self._on_change:
            self._on_change(self._theme)

    @property
    def is_dark(self) -> bool:
        return self._theme in ("dark", "high_contrast")

    def set_theme(self, theme: str) -> None:
        self.theme = theme

    def toggle(self) -> None:
        mapping = {"light": "dark", "dark": "light", "system": "light", "high_contrast": "dark"}
        self._theme = mapping.get(self._theme, "light")
        if self._on_change:
            self._on_change(self._theme)

    def set_dark(self, dark: bool) -> None:
        self._theme = "dark" if dark else "light"
        if self._on_change:
            self._on_change(self._theme)

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback
