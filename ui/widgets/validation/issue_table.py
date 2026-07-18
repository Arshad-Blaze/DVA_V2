"""Issue explorer table widget (Sprint 7)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_issue_table(
    issues: List[Dict[str, Any]],
    total_count: int,
    on_search: Callable,
    on_filter: Callable,
    on_select: Callable,
) -> None:
    section_header("Issue Explorer")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label(f"{total_count} issues").classes("text-sm text-gray-500")
            with ui.row().classes("gap-2"):
                ui.input(placeholder="Search...",
                         on_change=lambda e: on_search(e.value)).props("dense outlined").classes("min-w-32")
                ui.select(["all", "error", "warning", "info"], value="all", label="Severity",
                          on_change=lambda e: on_filter(e.value)).props("dense outlined").classes("min-w-24")

        if not issues:
            ui.label("No issues match current filters").classes("text-sm text-gray-400 italic")
            return

        with ui.table(
            rows=issues,
            row_key="rule",
            columns=[
                {"name": "severity", "label": "Severity", "field": "severity", "align": "center"},
                {"name": "rule", "label": "Rule", "field": "rule", "align": "left"},
                {"name": "message", "label": "Message", "field": "message", "align": "left"},
                {"name": "affected_records", "label": "Records", "field": "affected_records", "align": "right"},
                {"name": "category", "label": "Category", "field": "category", "align": "left"},
            ],
            pagination={"rowsPerPage": 10},
        ).classes("w-full"):
            pass
