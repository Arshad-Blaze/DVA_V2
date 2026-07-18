"""Log viewer widget (Sprint 9)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


SEVERITY_COLORS = {
    "info": "blue",
    "warning": "orange",
    "error": "red",
    "critical": "darkred",
}


def render_log_viewer(
    logs: List[Dict[str, Any]],
    selected: Optional[Dict[str, Any]],
    log_sources: List[str],
    on_search: Callable,
    on_filter_severity: Callable,
    on_filter_source: Callable,
    on_select: Callable,
    on_export: Callable,
) -> None:
    section_header("Log Viewer")
    with ui.card().classes("w-full p-4"):
        # Filters
        with ui.row().classes("w-full items-center gap-2 mb-3"):
            ui.input("Search logs", placeholder="Search messages...",
                     on_change=lambda e: on_search(e.value)).props("outlined dense").classes("flex-1")
            ui.select(["all", "info", "warning", "error", "critical"],
                      value="all", label="Severity",
                      on_change=lambda e: on_filter_severity(e.value)).props("outlined dense").classes("w-32")
            opts = ["all"] + log_sources
            ui.select(opts, value="all", label="Source",
                      on_change=lambda e: on_filter_source(e.value)).props("outlined dense").classes("w-32")
            ui.button("Export", icon="download", on_click=on_export).props("flat dense")

        # Log entries
        with ui.column().classes("w-full max-h-64 overflow-y-auto"):
            if not logs:
                ui.label("No logs match the current filters.").classes("text-sm text-gray-500 p-2")
            else:
                for i, log in enumerate(logs):
                    is_sel = selected and selected.get("timestamp") == log.get("timestamp")
                    sev = log.get("severity", "info")
                    color = SEVERITY_COLORS.get(sev, "gray")
                    cls = "p-2 border-l-4 cursor-pointer hover:bg-gray-50" + (" bg-blue-50" if is_sel else f" border-{color}-400")
                    with ui.row().classes(f"w-full {cls}").on("click", lambda idx=i: on_select(idx)):
                        with ui.column().classes("gap-0"):
                            ui.label(log.get("timestamp", "")).classes("text-xs text-gray-500")
                            ui.label(log.get("message", "")).classes("text-sm")
                            with ui.row().classes("gap-2"):
                                ui.badge(log.get("severity", ""), color=color).props("outline")
                                ui.label(log.get("source", "")).classes("text-xs text-gray-500")
