"""Mapping validation checklist widget."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_validation_checks(checks: List[Dict[str, Any]]) -> None:
    section_header("Mapping Validation")
    with ui.card().classes("w-full p-4"):
        with ui.column().classes("w-full gap-2"):
            for c in checks:
                icon_map = {"pass": "check_circle", "info": "info", "warning": "warning", "error": "error"}
                color_map = {"pass": "green", "info": "blue", "warning": "orange", "error": "red"}
                with ui.row().classes("items-center gap-3 py-1"):
                    ui.icon(icon_map.get(c["status"], "info"), color=color_map.get(c["status"], "grey")).classes("text-lg")
                    with ui.column().classes("gap-0"):
                        ui.label(c["label"]).classes("text-sm font-semibold")
                        ui.label(c["detail"]).classes("text-xs text-gray-500")
