"""Execution summary widget for Validation Center (Sprint 7)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_execution_summary() -> None:
    section_header("Execution Summary")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Status", "Completed", "check_circle", "green")
            metric_card("Rows Processed", "1,250", "table_rows", "blue")
            metric_card("Runtime", "4.2s", "timer", "orange")
            metric_card("Reports", "5 generated", "assessment", "blue")
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label("Completed: 2026-07-19 14:32:05").classes("text-xs text-gray-500")
            ui.label("·").classes("text-xs text-gray-300")
            ui.label("0 execution warnings").classes("text-xs text-gray-500")
