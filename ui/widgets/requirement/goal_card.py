"""Business goal selection card widget."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_goal_selection(
    goals: List[Dict[str, Any]],
    selected_id: Optional[str],
    on_select: Callable,
) -> None:
    section_header("Business Goal")
    with ui.card().classes("w-full p-4"):
        ui.label("What do you want to accomplish?").classes("text-sm text-gray-500 mb-3")
        with ui.grid(columns=3).classes("w-full gap-3"):
            for goal in goals:
                is_selected = goal["id"] == selected_id
                cls = "border-2 cursor-pointer p-3 rounded-lg transition-all"
                cls += " border-primary bg-primary-50" if is_selected else " border-gray-200 hover:border-primary"
                with ui.card().classes(cls).props("clickable") as card:
                    with ui.column().classes("items-center gap-1"):
                        ui.icon(goal.get("icon", "tab"), color="primary" if is_selected else "grey").classes("text-3xl")
                        ui.label(goal["label"]).classes("text-sm font-semibold text-center")
                        ui.label(goal["description"]).classes("text-xs text-gray-500 text-center")
                        ui.badge(goal["complexity"], color="blue" if goal["complexity"] == "Low" else ("orange" if goal["complexity"] == "Medium" else "red")).classes("text-xs")
                    if is_selected:
                        ui.icon("check_circle", color="primary").classes("absolute top-1 right-1 text-lg")
                card.on("click", lambda g=goal["id"]: on_select(g))
