"""Session controller — manages user session state."""

from typing import Any, Dict, Optional

from nicegui import ui
from ui.services.session_service import SessionService
from ui.services.theme_service import ThemeService


class SessionController:
    """Controls session state and preferences."""

    def __init__(self, session: SessionService, theme: ThemeService):
        self._session = session
        self._theme = theme

    def toggle_theme(self) -> None:
        self._theme.toggle()
        self._session.theme = "dark" if self._theme.is_dark else "light"
        ui.dark_mode().enable() if self._theme.is_dark else ui.dark_mode().disable()

    def toggle_sidebar(self) -> None:
        self._session.sidebar_collapsed = not self._session.sidebar_collapsed

    def toggle_inspector(self) -> None:
        self._session.inspector_visible = not self._session.inspector_visible
