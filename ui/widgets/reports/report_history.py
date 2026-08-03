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
        columns = [
            {"name": "execution_id", "label": "Execution ID", "field": "execution_id", "sortable": True},
            {"name": "generated", "label": "Generated", "field": "generated"},
            {"name": "version", "label": "Version", "field": "version"},
            {"name": "format", "label": "Format", "field": "format"},
            {"name": "status", "label": "Status", "field": "status"},
            {"name": "reports", "label": "Reports", "field": "reports"},
        ]
        rows = [
            {
                "execution_id": h.get("execution_id", "—"),
                "generated": h.get("generated", "—"),
                "version": h.get("version", "—"),
                "format": h.get("format", "—"),
                "status": h.get("status", "—"),
                "reports": str(h.get("reports", 0)),
            }
            for h in history
        ]
        with ui.table(rows=rows, columns=columns, row_key="execution_id").classes("w-full text-sm") as table:
            table.add_slot(
                "body-cell-status",
                '<td :props="props">'
                '<q-badge :color="props.value === \'completed\' ? \'green\' : \'orange\'" :label="props.value" />'
                "</td>",
            )
