"""About section widget (Sprint 9)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header


def render_about_section(about: Dict[str, Any]) -> None:
    section_header("About")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=2).classes("w-full gap-3"):
            for key, value in about.items():
                with ui.row().classes("items-center"):
                    ui.label(key.replace("_", " ").title() + ":").classes("text-sm font-medium w-32 text-gray-500")
                    ui.label(str(value)).classes("text-sm")
