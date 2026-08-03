"""Shell — Workspace manager.

Handles workspace content switching via the workspace controller.
"""

from nicegui import ui
from ui.controllers.workspace_controller import WorkspaceController


class WorkspaceManager:
    """Manages workspace content area and switching."""

    def __init__(self, ws_ctrl: WorkspaceController):
        self._ws_ctrl = ws_ctrl

    def create_container(self) -> ui.column:
        container = ui.column().classes("w-full h-full p-6 overflow-y-auto")
        self._ws_ctrl.set_container(container)
        return container

    def switch_to(self, workspace_id: str) -> None:
        self._ws_ctrl.render_current()
