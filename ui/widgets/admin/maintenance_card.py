"""Maintenance card widget (Sprint 9)."""

from typing import Any, Callable, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_maintenance_card(
    actions: List[Dict[str, Any]],
    on_run: Callable,
) -> None:
    section_header("Maintenance")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=2).classes("w-full gap-3"):
            for action in actions:
                sev = action.get("severity", "info")
                color = "red" if sev == "warning" else "blue"
                with ui.card().classes("p-3 cursor-pointer hover:shadow-md"
                                       ).on("click", lambda a=action["id"]: on_run(a)):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon(action.get("icon", "build"), color=color, size="md")
                        ui.label(action["label"]).classes("text-sm font-medium")
                    ui.label(action.get("description", "")).classes("text-xs text-gray-500 mt-1")
