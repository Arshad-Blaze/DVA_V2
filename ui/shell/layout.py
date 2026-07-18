"""Shell — Application layout.

Assembles the full application shell (header, sidebar, workspace, inspector, statusbar).
"""

from typing import Callable

from nicegui import ui
from ui.shell.header import create_header
from ui.shell.sidebar import create_sidebar
from ui.shell.statusbar import create_statusbar
from ui.shell.workspace_manager import WorkspaceManager
from ui.controllers.navigation_controller import NavigationController
from ui.controllers.workspace_controller import WorkspaceController
from ui.controllers.session_controller import SessionController
from ui.services.session_service import SessionService


def create_layout(
    session_svc: SessionService,
    session_ctrl: SessionController,
    nav_ctrl: NavigationController,
    ws_ctrl: WorkspaceController,
    ws_manager: WorkspaceManager,
    on_navigate: Callable,
) -> None:

    create_header(session_ctrl, session_svc)

    with ui.left_drawer(value=True).classes("bg-gray-900 text-white") as left_drawer:
        ui.label("Navigation").classes("text-xs uppercase tracking-wider text-gray-400 px-4 pt-4 pb-2")
        create_sidebar(nav_ctrl, on_navigate)

    with ui.right_drawer(value=True).classes("bg-gray-50") as right_drawer:
        ui.label("Inspector").classes("text-xs uppercase tracking-wider text-gray-400 px-4 pt-4 pb-2")
        with ui.column().classes("px-2 gap-3 w-full"):
            with ui.card().classes("w-full p-3"):
                ui.label("Session Info").classes("text-sm font-semibold")
                ui.label(f"Workspace: {session_svc.current_workspace.title()}").classes("text-xs text-gray-500")
                ui.label(f"Project: {'None' if not session_svc.current_project else session_svc.current_project}").classes("text-xs text-gray-500")
            with ui.card().classes("w-full p-3"):
                ui.label("Notifications").classes("text-sm font-semibold")
                ui.label("No new notifications").classes("text-xs text-gray-400")

    create_statusbar(session_svc)

    ws_manager.create_container()
    ws_ctrl.render_current()
