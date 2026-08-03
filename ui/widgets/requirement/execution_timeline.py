"""Execution timeline widget."""

from typing import List
from nicegui import ui
from ui.widgets.cards import section_header
from dav_platform.core.contracts import ExecutionStep


def render_execution_timeline(steps: List[ExecutionStep]) -> None:
    section_header("Execution Plan")
    if not steps:
        with ui.card().classes("w-full p-4"):
            ui.label("Select a business goal to generate an execution plan").classes("text-sm text-gray-500")
        return

    with ui.card().classes("w-full p-4"):
        for i, step in enumerate(steps):
            with ui.row().classes("items-start gap-3"):
                with ui.column().classes("items-center min-w-8"):
                    ui.badge(str(step.step_number), color="primary" if step.required else "grey").classes("text-xs")
                with ui.card().classes("flex-1 p-3 border-l-2").props("flat bordered"):
                    with ui.row().classes("items-center justify-between"):
                        ui.label(step.action).classes("text-sm font-semibold")
                        if not step.required:
                            ui.badge("Optional", color="grey").classes("text-xs")
                    ui.label(step.description).classes("text-xs text-gray-500")
                    ui.label(f"Layer: {step.layer}").classes("text-xs text-gray-400")
            if i < len(steps) - 1:
                with ui.column().classes("items-center ml-3"):
                    ui.icon("arrow_downward", color="grey").classes("text-lg")
