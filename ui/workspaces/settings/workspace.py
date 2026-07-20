"""Settings workspace — Platform configuration."""

from nicegui import ui
from ui.widgets.cards import section_header
from ui.shared import theme_svc, context
from ui.widgets.guidance_bar import render_guidance


def render():
    render_guidance("settings")

    t = theme_svc()

    section_header("Theme")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center gap-4"):
            ui.label("Dark Mode").classes("text-sm font-medium")
            ui.switch(value=t.is_dark, on_change=lambda e: t.set_theme("dark" if e.value else "light"))

        with ui.row().classes("items-center gap-4 mt-3"):
            ui.label("Theme:").classes("text-sm text-gray-500")
            ui.select(["light", "dark", "system", "high_contrast"], value=t.theme,
                      on_change=lambda e: t.set_theme(e.value)).classes("min-w-32")

    section_header("Workspace Preferences")
    with ui.card().classes("w-full p-4"):
        ui.label("Settings are managed through the Administration workspace.").classes("text-sm text-gray-500")
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.icon("info", color="info").classes("text-sm")
            ui.label("Go to Administration → Settings for detailed preferences.").classes("text-xs text-gray-400")

    section_header("About")
    with ui.card().classes("w-full p-4"):
        ui.label("DVA Platform v2.0").classes("text-lg font-bold")
        ui.label("Data Validation & Analytics Platform").classes("text-sm text-gray-500")
        ui.label("9-Layer Pipeline Architecture").classes("text-xs text-gray-400 mt-1")
        ui.label("NiceGUI + Python 3.12").classes("text-xs text-gray-400")
