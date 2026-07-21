from nicegui import ui
from ui.shared import demo_svc


THEME_ICONS = {
    "light": "light_mode",
    "dark": "dark_mode",
    "system": "brightness_auto",
    "high_contrast": "contrast",
}


def _theme_icon(theme: str) -> str:
    return THEME_ICONS.get(theme, "dark_mode")


def create_header(session_ctrl, session_svc) -> None:
    with ui.header().classes("items-center justify-between px-4 py-2"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("dataset_linked", color="white").classes("text-xl")
            ui.label("DVA Platform").classes("text-lg font-bold text-white")
            ui.label(f"|  {session_svc.current_workspace.title()}").classes("text-sm text-gray-300")
            if demo_svc().is_active:
                with ui.row().classes("items-center gap-1 ml-4 bg-amber-500 text-black px-3 py-1 rounded-full"):
                    ui.icon("science").classes("text-sm")
                    ui.label("Demo Mode").classes("text-xs font-bold uppercase tracking-wider")

        with ui.row().classes("items-center gap-2"):
            status = session_svc.execution_status
            color = "green" if status == "idle" else "orange"
            ui.html(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};"></span>')
            ui.label(status.title()).classes("text-xs text-gray-300")
            ui.button(icon=_theme_icon(session_svc.theme), on_click=session_ctrl.toggle_theme).props("flat round dense color=white").tooltip("Toggle theme")
            ui.button(icon="settings", on_click=lambda: None).props("flat round dense color=white").tooltip("Settings")
