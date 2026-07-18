"""Recommendation display widget."""

from typing import Any, Callable, Dict
from nicegui import ui
from ui.widgets.cards import section_header


def render_recommendation(
    recommendation: Dict[str, Any],
    accepted: bool,
    on_accept: Callable,
    on_change_goal: Callable,
) -> None:
    section_header("Recommended Workflow")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-start gap-4 w-full"):
            with ui.column().classes("flex-1 gap-2"):
                ui.label(recommendation.get("workflow", "No recommendation")).classes("text-sm font-semibold")
                ui.label(f"Confidence: {recommendation.get('confidence', 0):.0%}").classes("text-xs text-gray-500")
                ui.label(f"Why: {recommendation.get('reason', '')}").classes("text-xs text-gray-400")
                if recommendation.get("alternatives"):
                    ui.label("Alternatives: " + ", ".join(recommendation["alternatives"])).classes("text-xs text-blue-500")
            with ui.column().classes("items-end gap-2 min-w-32"):
                if accepted:
                    ui.badge("✓ Accepted", color="green").classes("text-sm")
                else:
                    ui.button("Accept", on_click=on_accept, icon="thumb_up").props("outline").classes("text-sm")
                ui.button("Change Goal", on_click=on_change_goal, icon="refresh").props("flat").classes("text-sm")
