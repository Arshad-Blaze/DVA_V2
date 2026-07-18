"""DVA Platform UI — Application Entry Point.

UI Sprint 1: Application Shell & Workspace Framework.
"""

from nicegui import app, ui

from ui.controllers.navigation_controller import NavigationController
from ui.controllers.session_controller import SessionController
from ui.controllers.workspace_controller import WorkspaceController
from ui.services.navigation_service import NavigationService
from ui.services.notification_service import NotificationService
from ui.services.session_service import SessionService
from ui.services.theme_service import ThemeService
from ui.shell.layout import create_layout
from ui.shell.workspace_manager import WorkspaceManager
from ui.styles.custom import CUSTOM_CSS

# Workspace imports
from ui.workspaces.home.workspace import render as render_home
from ui.workspaces.projects.workspace import render as render_projects
from ui.workspaces.connection.workspace import render as render_connection
from ui.workspaces.detection.workspace import render as render_detection
from ui.workspaces.canonical.workspace import render as render_canonical
from ui.workspaces.requirement.workspace import render as render_requirement
from ui.workspaces.operation.workspace import render as render_operation
from ui.workspaces.processing.workspace import render as render_processing
from ui.workspaces.validation.workspace import render as render_validation
from ui.workspaces.reports.workspace import render as render_reports
from ui.workspaces.settings.workspace import render as render_settings
from ui.workspaces.help.workspace import render as render_help

# Singletons
session_svc = SessionService()
nav_svc = NavigationService()
notify_svc = NotificationService()
theme_svc = ThemeService()

# Controllers
session_ctrl = SessionController(session_svc, theme_svc)
nav_ctrl = NavigationController(nav_svc)
ws_ctrl = WorkspaceController(session_svc, nav_svc)
ws_manager = WorkspaceManager(ws_ctrl)


def on_navigate(workspace_id: str) -> None:
    nav_svc.navigate(workspace_id)
    session_svc.current_workspace = workspace_id
    ws_manager.switch_to(workspace_id)


@ui.page("/")
def main():
    ui.add_head_html(f"<style>{CUSTOM_CSS}</style>")
    ui.dark_mode().disable()

    # Register all workspaces with the content controller
    ws_ctrl.register("home", render_home)
    ws_ctrl.register("projects", render_projects)
    ws_ctrl.register("connection", render_connection)
    ws_ctrl.register("detection", render_detection)
    ws_ctrl.register("canonical", render_canonical)
    ws_ctrl.register("requirement", render_requirement)
    ws_ctrl.register("operation", render_operation)
    ws_ctrl.register("processing", render_processing)
    ws_ctrl.register("validation", render_validation)
    ws_ctrl.register("reports", render_reports)
    ws_ctrl.register("settings", render_settings)
    ws_ctrl.register("help", render_help)

    create_layout(
        session_svc=session_svc,
        session_ctrl=session_ctrl,
        nav_ctrl=nav_ctrl,
        ws_ctrl=ws_ctrl,
        ws_manager=ws_manager,
        on_navigate=on_navigate,
    )


app.on_startup(lambda: None)

if __name__ == "__main__":
    ui.run(title="DVA Platform v2", reload=False, host="0.0.0.0", port=8080)
