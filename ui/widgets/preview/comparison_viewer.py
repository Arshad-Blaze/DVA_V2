"""Side-by-side comparison viewer widget."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_comparison(rows: List[Dict[str, Any]]) -> None:
    section_header("Side-by-Side Comparison")
    with ui.card().classes("w-full p-4"):
        ui.label("Retailer Schema vs Business Schema").classes("text-sm text-gray-500 mb-3")

        with ui.grid(columns=2).classes("w-full gap-6"):
            with ui.column().classes("w-full"):
                ui.label("Retailer Schema").classes("text-sm font-semibold mb-2 text-blue-600")
                with ui.table(rows=rows, row_key="physical", columns=[
                    {"name": "physical", "label": "Original Column", "field": "physical", "align": "left"},
                    {"name": "sample", "label": "Sample Value", "field": "sample", "align": "left"},
                ]).classes("w-full"):
                    pass

            with ui.column().classes("w-full"):
                ui.label("Business Schema").classes("text-sm font-semibold mb-2 text-green-600")
                with ui.table(rows=rows, row_key="physical", columns=[
                    {"name": "business", "label": "Canonical Field", "field": "business", "align": "left"},
                    {"name": "business_sample", "label": "Canonical Value", "field": "business_sample", "align": "left"},
                ]).classes("w-full"):
                    pass
