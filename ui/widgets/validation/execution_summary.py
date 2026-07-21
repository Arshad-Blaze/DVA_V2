"""Execution summary widget for Validation Center (Sprint 7)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card
from ui.shared import proc_svc


def render_execution_summary() -> None:
    section_header("Execution Summary")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            summary = proc_svc().results_summary
            rows = f"{summary['rows_processed']:,}"
            metric_card("Status", summary.get("state", "Pending").title(), "check_circle", "green")
            metric_card("Rows Processed", rows, "table_rows", "blue")
            metric_card("Runtime", f"{proc_svc().elapsed_seconds:.1f}s", "timer", "orange")
            metric_card("Reports", "Pending", "assessment", "blue")
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label(f"Warnings: {summary.get('warnings', 0)}").classes("text-xs text-gray-500")
            ui.label("·").classes("text-xs text-gray-300")
            ui.label(f"Errors: {summary.get('errors', 0)}").classes("text-xs text-gray-500")
