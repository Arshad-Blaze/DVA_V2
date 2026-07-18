"""Validation timeline widget (Sprint 7)."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_timeline(stages: List[Dict[str, Any]]) -> None:
    section_header("Validation Timeline")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between w-full"):
            for i, stage in enumerate(stages):
                status = stage.get("status", "pending")
                icon_map = {"completed": "check_circle", "current": "arrow_circle_right", "pending": "circle"}
                color_map = {"completed": "green", "current": "primary", "pending": "grey"}
                with ui.column().classes("items-center gap-1 min-w-20"):
                    ui.icon(icon_map.get(status, "circle"), color=color_map.get(status, "grey")).classes("text-2xl")
                    ui.label(stage.get("label", "")).classes("text-xs text-center font-semibold")
                if i < len(stages) - 1:
                    c = "green" if status == "completed" else "grey"
                    ui.icon("arrow_forward", color=c).classes("text-lg")
