"""Workspace controller — manages workspace lifecycle and content."""

import importlib
from typing import Callable, Dict, Optional, Tuple, Union

from nicegui import ui
from ui.services.session_service import SessionService
from ui.services.navigation_service import NavigationService

LazyEntry = Tuple[str, str]


class WorkspaceController:
    """Controls workspace content rendering."""

    def __init__(self, session: SessionService, nav: NavigationService):
        self._session = session
        self._nav = nav
        self._registry: Dict[str, Union[Callable, LazyEntry]] = {}
        self._content_container: Optional[ui.column] = None

    def register(self, workspace_id: str, render_fn: Union[Callable, LazyEntry]) -> None:
        self._registry[workspace_id] = render_fn

    def set_container(self, container: ui.column) -> None:
        self._content_container = container

    def render_current(self) -> None:
        if self._content_container is None:
            return
        self._content_container.clear()
        workspace_id = self._nav.active
        entry = self._registry.get(workspace_id)
        if entry is None:
            with self._content_container:
                ui.label(f"Workspace '{workspace_id}' not registered").classes("text-gray-500")
            return
        render_fn = self._resolve(entry)
        if render_fn:
            with self._content_container:
                render_fn()

    def _resolve(self, entry: Union[Callable, LazyEntry]) -> Optional[Callable]:
        if isinstance(entry, tuple):
            module_path, func_name = entry
            try:
                module = importlib.import_module(module_path)
                return getattr(module, func_name)
            except (ImportError, AttributeError):
                return None
        return entry
