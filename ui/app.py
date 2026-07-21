from nicegui import app, ui

from ui import shared
from ui.controllers.workspace_controller import WorkspaceController
from ui.shell.layout import create_layout
from ui.shell.workspace_manager import WorkspaceManager
from ui.styles.custom import CUSTOM_CSS
from ui.themes.dark import css_vars as dark_css
from ui.themes.light import css_vars as light_css
from ui.themes.high_contrast import css_vars as hc_css

from ui.workspaces.welcome.welcome_wizard import WelcomeWizard


def _auto_save() -> None:
    persistence = shared.persistence()
    persistence.save_session()


def on_navigate(workspace_id: str) -> None:
    nav_svc.navigate(workspace_id)
    session_svc.current_workspace = workspace_id
    ws_manager.switch_to(workspace_id)
    _auto_save()


def _on_wizard_complete() -> None:
    ctx = shared.context()
    ctx.wizard_completed = True
    if demo_svc.is_active:
        ctx.current_workspace = "detection"
    _auto_save()
    ui.navigate.reload()


# Initialize all shared services (loads persisted session/projects/connections)
shared.init_all()
shared.perf_svc().record_startup()

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

welcome_svc = shared.welcome_svc()
demo_svc = shared.demo_svc()


@ui.page("/")
def main():
    ui.add_head_html(f"<style>{CUSTOM_CSS}</style>")

    theme = theme_svc.theme
    if theme == "dark":
        ui.dark_mode().enable()
        additional_css = f":root {{\n{dark_css}\n}}"
    elif theme == "high_contrast":
        ui.dark_mode().enable()
        additional_css = f":root {{\n{hc_css}\n}}"
    elif theme == "system":
        ui.dark_mode().auto()
        additional_css = ""
    else:
        ui.dark_mode().disable()
        additional_css = f":root {{\n{light_css}\n}}"

    if additional_css:
        ui.add_head_html(f"<style>{additional_css}</style>")

    ctx = shared.context()
    if not ctx.wizard_completed:
        wizard = WelcomeWizard(
            welcome_service=welcome_svc,
            theme_service=theme_svc,
            project_service=shared.project_svc(),
            connection_service=shared.conn_svc(),
            demo_service=demo_svc,
            on_complete=_on_wizard_complete,
        )
        with ui.column().classes("w-full min-h-screen items-center justify-center p-8"):
            wizard.render(ui.column())
        return

    ws_ctrl.register("home", ("ui.workspaces.home.workspace", "render"))
    ws_ctrl.register("projects", ("ui.workspaces.projects.workspace", "render"))
    ws_ctrl.register("connection", ("ui.workspaces.connection.workspace", "render"))
    ws_ctrl.register("detection", ("ui.workspaces.detection.workspace", "render"))
    ws_ctrl.register("canonical", ("ui.workspaces.canonical.workspace", "render"))
    ws_ctrl.register("preview", ("ui.workspaces.preview.workspace", "render"))
    ws_ctrl.register("requirement", ("ui.workspaces.requirement.workspace", "render"))
    ws_ctrl.register("operation", ("ui.workspaces.operation.workspace", "render"))
    ws_ctrl.register("processing", ("ui.workspaces.processing.workspace", "render"))
    ws_ctrl.register("validation", ("ui.workspaces.validation.workspace", "render"))
    ws_ctrl.register("reports", ("ui.workspaces.reports.workspace", "render"))
    ws_ctrl.register("administration", ("ui.workspaces.administration.workspace", "render"))
    ws_ctrl.register("settings", ("ui.workspaces.settings.workspace", "render"))
    ws_ctrl.register("help", ("ui.workspaces.help.workspace", "render"))
    ws_ctrl.register("developer", ("ui.workspaces.developer.workspace", "render"))
    ws_ctrl.register("health", ("ui.workspaces.health.workspace", "render"))

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
