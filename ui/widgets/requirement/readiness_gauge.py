"""Readiness gauge widget."""

from typing import Dict
from nicegui import ui
from ui.widgets.cards import section_header


def render_readiness_gauge(readiness: Dict[str, bool], overall: str) -> None:
    section_header("Readiness Dashboard")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label("Overall Readiness").classes("text-sm font-semibold")
            color_map = {"Ready": "green", "Almost Ready": "orange", "Review Required": "red"}
            ui.badge(overall, color=color_map.get(overall, "grey")).classes("text-sm")

        items = [
            ("project_ready", "Project Ready"),
            ("connection_ready", "Connection Ready"),
            ("detection_ready", "Detection Ready"),
            ("canonical_ready", "Business Mapping Ready"),
            ("preview_approved", "Business Preview Approved"),
            ("requirement_complete", "Requirement Complete"),
        ]

        with ui.grid(columns=3).classes("w-full gap-3"):
            for key, label in items:
                ready = readiness.get(key, False)
                cls = "border rounded-lg p-3 "
                cls += "border-green-200 bg-green-50" if ready else "border-gray-200 bg-gray-50"
                with ui.card().classes(cls):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle" if ready else "radio_button_unchecked",
                                color="green" if ready else "grey").classes("text-lg")
                        ui.label(label).classes("text-xs font-semibold")
