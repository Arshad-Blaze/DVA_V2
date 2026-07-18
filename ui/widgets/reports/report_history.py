"""Report history widget (Sprint 8)."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_report_history(history: List[Dict[str, Any]]) -> None:
    section_header("Report History")
    with ui.card().classes("w-full p-4"):
        if not history:
            ui.label("No report history available.").classes("text-sm text-gray-500")
            return
        with ui.table(rows=history, row_key="execution_id").classes("w-full text-sm"):
            with ui.thead():
                with ui.tr():
                    ui.th().text("Execution ID")
                    ui.th().text("Generated")
                    ui.th().text("Version")
                    ui.th().text("Format")
                    ui.th().text("Status")
                    ui.th().text("Reports")
            with ui.tbody():
                for h in history:
                    with ui.tr():
                        ui.td().text(h.get("execution_id", "—"))
                        ui.td().text(h.get("generated", "—"))
                        ui.td().text(h.get("version", "—"))
                        ui.td().text(h.get("format", "—"))
                        with ui.td():
                            status = h.get("status", "—")
                            color = "green" if status == "completed" else "orange"
                            ui.badge(status, color=color)
                        ui.td().text(str(h.get("reports", 0)))
