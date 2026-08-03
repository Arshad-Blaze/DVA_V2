"""Pipeline visualization widget."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_pipeline(stages: List[Dict[str, Any]], current_index: int) -> None:
    section_header("Transformation Pipeline")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between w-full"):
            for i, stage in enumerate(stages):
                is_current = i == current_index
                is_completed = i < current_index
                cls = "text-green-600" if is_completed else ""
                cls = "text-primary font-bold" if is_current else cls
                cls = "text-gray-400" if i > current_index else cls
                with ui.column().classes("items-center gap-1 min-w-20"):
                    icon = stage["icon"]
                    if is_completed:
                        icon = "check_circle"
                    elif is_current:
                        icon = "arrow_circle_right"
                    ui.icon(icon, color="primary" if is_current else ("green" if is_completed else "grey")).classes("text-2xl")
                    ui.label(stage["label"]).classes(f"text-xs text-center {cls}")
                if i < len(stages) - 1:
                    ui.icon("chevron_right", color="grey").classes("text-lg")
