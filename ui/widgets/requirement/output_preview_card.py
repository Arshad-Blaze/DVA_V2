"""Expected outputs preview widget."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_output_preview(outputs: List[str], estimates: Dict[str, Any]) -> None:
    section_header("Expected Outputs & Estimates")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=2).classes("w-full gap-6"):
            with ui.column().classes("w-full gap-2"):
                ui.label("Deliverables").classes("text-sm font-semibold mb-2")
                if outputs:
                    for out in outputs:
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("description", color="blue").classes("text-lg")
                            ui.label(out).classes("text-sm")
                else:
                    ui.label("No outputs specified").classes("text-sm text-gray-500")

            with ui.column().classes("w-full gap-2"):
                ui.label("Execution Estimates").classes("text-sm font-semibold mb-2")
                for key, label in [
                    ("runtime", "Estimated Runtime"),
                    ("complexity", "Processing Complexity"),
                    ("memory", "Memory Estimate"),
                    ("report_count", "Expected Reports"),
                    ("validation_rules", "Validation Rules"),
                ]:
                    with ui.row().classes("items-center justify-between py-1"):
                        ui.label(label).classes("text-xs text-gray-500")
                        ui.label(str(estimates.get(key, "-"))).classes("text-xs font-semibold")
                streaming = estimates.get("streaming", False)
                with ui.row().classes("items-center gap-2"):
                    ui.label("Streaming").classes("text-xs text-gray-500")
                    ui.icon("check", color="green").classes("text-sm") if streaming else ui.icon("close", color="red").classes("text-sm")
