"""Suggested actions recommendation panel (Sprint 7)."""

from typing import Any, Callable, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_recommendations(
    actions: List[Dict[str, Any]],
    on_navigate: Callable,
) -> None:
    section_header("Suggested Actions")
    if not actions:
        with ui.card().classes("w-full p-4"):
            ui.label("No actions suggested").classes("text-sm text-gray-500")
        return

    with ui.card().classes("w-full p-4"):
        with ui.column().classes("w-full gap-2"):
            for a in actions:
                severity = a.get("severity", "info")
                icon_map = {"error": "error", "warning": "warning", "info": "info"}
                color_map = {"error": "red", "warning": "orange", "info": "blue"}
                with ui.row().classes("items-center gap-3 py-2 border-b border-gray-100"):
                    ui.icon(icon_map.get(severity, "info"), color=color_map.get(severity, "grey")).classes("text-lg")
                    with ui.column().classes("flex-1 gap-0"):
                        ui.label(a.get("action", "")).classes("text-sm font-semibold")
                        ui.label(a.get("reason", "")).classes("text-xs text-gray-500")
                    nav = a.get("navigate", "")
                    if nav:
                        ui.button("Go", icon="arrow_forward",
                                  on_click=lambda w=nav: on_navigate(w)).props("flat dense")
