"""DVA Platform UI — Application Entry Point.

UI Sprint 2.5: Persistence Foundation & Workspace Context.
Saves/restores session, projects, and connections across application restarts.
"""

from nicegui import app, ui

from ui import shared
from ui.controllers.workspace_controller import WorkspaceController
from ui.shell.layout import create_layout
from ui.shell.workspace_manager import WorkspaceManager
from ui.styles.custom import CUSTOM_CSS

# Workspace imports
from ui.workspaces.home.workspace import render as render_home
from ui.workspaces.projects.workspace import render as render_projects
from ui.workspaces.connection.workspace import render as render_connection
from ui.workspaces.detection.workspace import render as render_detection
from ui.workspaces.canonical.workspace import render as render_canonical
from ui.workspaces.preview.workspace import render as render_preview
from ui.workspaces.requirement.workspace import render as render_requirement
from ui.workspaces.operation.workspace import render as render_operation
from ui.workspaces.processing.workspace import render as render_processing
from ui.workspaces.validation.workspace import render as render_validation
from ui.workspaces.reports.workspace import render as render_reports
from ui.workspaces.administration.workspace import render as render_administration
from ui.workspaces.settings.workspace import render as render_settings
from ui.workspaces.help.workspace import render as render_help


# Initialize all shared services (loads persisted session/projects/connections)
shared.init_all()

# Wire global navigation handler for workspace-to-workspace navigation
shared.set_navigate_handler(on_navigate)

session_svc = shared.session_svc()
nav_svc = shared.nav_svc()
notify_svc = shared.notify_svc()
theme_svc = shared.theme_svc()

# Controllers
session_ctrl = shared.session_ctrl()
nav_ctrl = shared.nav_ctrl()
ws_ctrl = shared.ws_ctrl()
ws_manager = WorkspaceManager(ws_ctrl)


def on_navigate(workspace_id: str) -> None:
    nav_svc.navigate(workspace_id)
    session_svc.current_workspace = workspace_id
    ws_manager.switch_to(workspace_id)
    _auto_save()


def _auto_save() -> None:
    """Persist current session state on navigation changes."""
    persistence = shared.persistence()
    persistence.save_session()


@ui.page("/")
def main():
    ui.add_head_html(f"<style>{CUSTOM_CSS}</style>")
    ui.dark_mode().enable() if theme_svc.is_dark else ui.dark_mode().disable()

    # Register all workspaces
    ws_ctrl.register("home", render_home)
    ws_ctrl.register("projects", render_projects)
    ws_ctrl.register("connection", render_connection)
    ws_ctrl.register("detection", render_detection)
    ws_ctrl.register("canonical", render_canonical)
    ws_ctrl.register("preview", render_preview)
    ws_ctrl.register("requirement", render_requirement)
    ws_ctrl.register("operation", render_operation)
    ws_ctrl.register("processing", render_processing)
    ws_ctrl.register("validation", render_validation)
    ws_ctrl.register("reports", render_reports)
    ws_ctrl.register("administration", render_administration)
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
