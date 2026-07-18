"""Interactive report viewer widget (Sprint 8)."""

from typing import Any, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_report_viewer(reports: List[Dict[str, Any]], selected: Optional[Dict[str, Any]]) -> None:
    section_header("Interactive Reports")
    if selected:
        with ui.card().classes("w-full p-4"):
            ui.label(selected["name"]).classes("text-lg font-semibold")
            ui.label(f"Type: {selected['type']}").classes("text-sm text-gray-500")
            ui.label(f"Sections: {', '.join(selected['sections'])}").classes("text-sm text-gray-500")
            ui.label(f"Available: {', '.join(selected.get('downloads', []))}").classes("text-sm text-gray-500")
            with ui.row().classes("gap-2 mt-2"):
                for sec in selected["sections"]:
                    ui.badge(sec.replace("_", " ").title(), color="blue").props("outline")
    else:
        with ui.card().classes("w-full p-4"):
            ui.label("Select a report from the explorer to view details.").classes("text-sm text-gray-500")
