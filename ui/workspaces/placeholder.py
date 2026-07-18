"""Reusable placeholder workspace for non-functional pages."""

from nicegui import ui


def render_placeholder(title: str, description: str, icon: str = "construction") -> None:
    with ui.column().classes("w-full items-center justify-center p-12"):
        ui.icon(icon, color="grey").classes("text-6xl")
        ui.label(title).classes("text-2xl font-semibold mt-4")
        ui.label(description).classes("text-gray-500 text-center max-w-md mt-2")
        ui.label("Coming in a future UI sprint").classes("text-xs text-gray-400 mt-2")
