from nicegui import ui
from ui.services.session_service import SessionService
from ui.services.theme_service import ThemeService


class SessionController:
    def __init__(self, session: SessionService, theme: ThemeService):
        self._session = session
        self._theme = theme

    def toggle_theme(self) -> None:
        cycle = ["light", "dark", "system", "high_contrast"]
        current = self._theme.theme
        idx = cycle.index(current) if current in cycle else 0
        next_theme = cycle[(idx + 1) % 4]
        self._theme.set_theme(next_theme)
        self._session.theme = next_theme
        if next_theme in ("dark", "high_contrast"):
            ui.dark_mode().enable()
        elif next_theme == "system":
            ui.dark_mode().auto()
        else:
            ui.dark_mode().disable()

    def toggle_sidebar(self) -> None:
        self._session.sidebar_collapsed = not self._session.sidebar_collapsed

    def toggle_inspector(self) -> None:
        self._session.inspector_visible = not self._session.inspector_visible
