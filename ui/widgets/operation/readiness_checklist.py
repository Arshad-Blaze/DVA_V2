"""Readiness checklist widget (Sprint 6A)."""

from typing import Any, Callable, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_readiness_checklist(items: List[Dict[str, Any]], overall: str) -> None:
    section_header("Execution Readiness")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label("Readiness Checklist").classes("text-sm font-semibold")
            color_map = {"Ready to Execute": "green", "Review Required": "red"}
            ui.badge(overall, color=color_map.get(overall, "grey")).classes("text-sm")

        with ui.grid(columns=2).classes("w-full gap-3"):
            for item in items:
                ready = item["status"]
                cls = "border rounded-lg p-3 "
                cls += "border-green-200 bg-green-50" if ready else "border-gray-200 bg-gray-50"
                with ui.card().classes(cls):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle" if ready else "radio_button_unchecked",
                                color="green" if ready else "grey").classes("text-lg")
                        ui.label(item["label"]).classes("text-xs font-semibold")
