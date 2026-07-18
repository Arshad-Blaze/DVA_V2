"""Shell — Application header."""

from nicegui import ui


def create_header(session_ctrl, session_svc) -> None:
    with ui.header().classes("items-center justify-between px-4 py-2"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("dataset_linked", color="white").classes("text-xl")
            ui.label("DVA Platform").classes("text-lg font-bold text-white")
            ui.label(f"|  {session_svc.current_workspace.title()}").classes("text-sm text-gray-300")

        with ui.row().classes("items-center gap-2"):
            status = session_svc.execution_status
            color = "green" if status == "idle" else "orange"
            ui.html(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};"></span>')
            ui.label(status.title()).classes("text-xs text-gray-300")
            ui.button(icon="dark_mode", on_click=session_ctrl.toggle_theme).props("flat round dense color=white")
            ui.button(icon="settings", on_click=lambda: None).props("flat round dense color=white")
