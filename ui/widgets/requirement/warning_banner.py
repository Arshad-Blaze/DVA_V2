"""Warning banner widget for Analysis Planner."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_warnings(warnings: List[Dict[str, Any]]) -> None:
    section_header("Warnings")
    if not warnings:
        with ui.card().classes("w-full p-4"):
            ui.label("No warnings — plan looks good!").classes("text-sm text-gray-500")
        return

    with ui.card().classes("w-full p-4"):
        for w in warnings:
            icon_map = {"error": "error", "warning": "warning", "info": "info"}
            color_map = {"error": "red", "warning": "orange", "info": "blue"}
            severity = w.get("severity", "info")
            with ui.row().classes("items-start gap-3 py-2 border-b border-gray-100"):
                ui.icon(icon_map.get(severity, "info"), color=color_map.get(severity, "grey")).classes("text-lg mt-0.5")
                with ui.column().classes("gap-0 flex-1"):
                    ui.label(w.get("problem", "")).classes("text-sm font-semibold")
                    ui.label(f"Impact: {w.get('impact', '')}").classes("text-xs text-gray-500")
                    ui.label(f"Recommendation: {w.get('recommendation', '')}").classes("text-xs text-blue-500")
