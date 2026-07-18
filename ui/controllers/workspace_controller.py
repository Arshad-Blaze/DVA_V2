"""Workspace controller — manages workspace lifecycle and content."""

from typing import Any, Callable, Dict, Optional

from nicegui import ui
from ui.services.session_service import SessionService
from ui.services.navigation_service import NavigationService


class WorkspaceController:
    """Controls workspace content rendering."""

    def __init__(self, session: SessionService, nav: NavigationService):
        self._session = session
        self._nav = nav
        self._registry: Dict[str, Callable] = {}
        self._content_container: Optional[ui.column] = None

    def register(self, workspace_id: str, render_fn: Callable) -> None:
        self._registry[workspace_id] = render_fn

    def set_container(self, container: ui.column) -> None:
        self._content_container = container

    def render_current(self) -> None:
        if self._content_container is None:
            return
        self._content_container.clear()
        workspace_id = self._nav.active
        render_fn = self._registry.get(workspace_id)
        if render_fn:
            with self._content_container:
                render_fn()
        else:
            with self._content_container:
                ui.label(f"Workspace '{workspace_id}' not registered").classes("text-gray-500")
