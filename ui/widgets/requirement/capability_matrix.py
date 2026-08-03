"""Capability matrix widget."""

from typing import Dict
from nicegui import ui
from ui.widgets.cards import section_header
from dav_platform.core.contracts import CapabilityMatrix


def render_capability_matrix(
    matrix: CapabilityMatrix,
    descriptions: Dict[str, Dict[str, str]],
) -> None:
    section_header("Capability Matrix")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=3).classes("w-full gap-3"):
            for key, desc in descriptions.items():
                enabled = getattr(matrix, key, False)
                icon = desc.get("icon", "tab")
                label = desc.get("label", key)
                cls = "border rounded-lg p-3 "
                if enabled:
                    cls += "border-green-200 bg-green-50"
                else:
                    cls += "border-gray-200 bg-gray-50 opacity-50"
                with ui.card().classes(cls):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon(icon, color="green" if enabled else "grey").classes("text-xl")
                        ui.label(label).classes("text-sm font-semibold")
                        if enabled:
                            ui.icon("check", color="green").classes("text-lg ml-auto")
                        else:
                            ui.icon("lock", color="grey").classes("text-lg ml-auto")
