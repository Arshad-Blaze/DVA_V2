"""Live log viewer widget (Sprint 6B)."""

from typing import List
from nicegui import ui
from ui.widgets.cards import section_header
from dav_platform.core.contracts import OperationLog


def render_log_viewer(logs: List[OperationLog]) -> None:
    section_header("Live Logs")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-2"):
            ui.label(f"{len(logs)} entries").classes("text-xs text-gray-500")
            with ui.row().classes("gap-2"):
                ui.input(placeholder="Search...").props("dense outlined").classes("min-w-24")
                ui.select(["All", "info", "warning", "error", "success"], value="All",
                          label="Level").props("dense outlined").classes("min-w-20")

        if not logs:
            ui.label("No log entries yet").classes("text-sm text-gray-400 italic")
            return

        with ui.scroll_area().classes("w-full max-h-64"):
            for log in reversed(logs):
                color_map = {"info": "blue", "warning": "orange", "error": "red", "success": "green"}
                color = color_map.get(log.level, "grey")
                with ui.row().classes("items-start gap-2 py-1 font-mono text-xs"):
                    ui.label(log.timestamp).classes(f"text-{color} min-w-20")
                    ui.badge(log.level.upper(), color=color).classes("text-xs min-w-16 text-center")
                    ui.label(f"[{log.action}]").classes("text-gray-500 min-w-24")
                    ui.label(log.message).classes("text-gray-700")
