"""Pipeline visualization widget (Sprint 6A)."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_pipeline_viz(stages: List[Dict[str, Any]]) -> None:
    section_header("Pipeline Visualization")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between w-full"):
            for i, stage in enumerate(stages):
                with ui.column().classes("items-center gap-1 min-w-20"):
                    ui.icon(stage.get("icon", "circle"), color="primary").classes("text-2xl")
                    ui.label(stage["label"]).classes("text-xs font-semibold text-center")
                    ui.label(stage.get("purpose", "")).classes("text-xs text-gray-400 text-center max-w-24")
                    ui.label(stage.get("duration", "")).classes("text-xs text-gray-500")
                if i < len(stages) - 1:
                    ui.icon("arrow_forward", color="grey").classes("text-lg")
