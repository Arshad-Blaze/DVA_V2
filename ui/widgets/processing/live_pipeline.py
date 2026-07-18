"""Live pipeline widget (Sprint 6B)."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_live_pipeline(stages: List[Dict[str, Any]]) -> None:
    section_header("Live Pipeline")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between w-full"):
            for i, stage in enumerate(stages):
                state = stage.get("state", "pending")
                icon_map = {"pending": "circle", "running": "autorenew", "completed": "check_circle",
                            "failed": "error", "cancelled": "cancel", "skipped": "skip_next"}
                color_map = {"pending": "grey", "running": "blue", "completed": "green",
                             "failed": "red", "cancelled": "grey", "skipped": "grey"}
                anim = "animate-spin" if state == "running" else ""
                with ui.column().classes("items-center gap-1 min-w-16"):
                    ui.icon(icon_map.get(state, "circle"), color=color_map.get(state, "grey")).classes(f"text-2xl {anim}")
                    ui.label(stage.get("label", "")).classes("text-xs font-semibold text-center")
                    elapsed = stage.get("elapsed", 0)
                    if elapsed > 0:
                        ui.label(f"{elapsed:.1f}s").classes("text-xs text-gray-400")
                if i < len(stages) - 1:
                    connector_color = "green" if state == "completed" else "grey"
                    ui.icon("arrow_forward", color=connector_color).classes("text-lg")
