"""Results summary widget (Sprint 6B)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_results_summary(results: Dict[str, Any]) -> None:
    section_header("Results Summary")
    with ui.card().classes("w-full p-4"):
        state = results.get("state", "pending")
        color_map = {"completed": "green", "running": "blue", "pending": "grey",
                     "failed": "red", "cancelled": "orange"}
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label("Processing Complete").classes("text-sm font-semibold")
            ui.badge(state.upper(), color=color_map.get(state, "grey")).classes("text-sm")

        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Rows Processed", f'{results.get("rows_processed", 0):,}', "table_rows", "blue")
            metric_card("Stores", str(results.get("stores", 0)), "store", "green")
            metric_card("UPCs", f'{results.get("upcs", 0):,}', "barcode", "green")
            metric_card("Categories", str(results.get("categories", 0)), "category", "orange")
        with ui.grid(columns=4).classes("w-full gap-4 mt-2"):
            metric_card("Brands", str(results.get("brands", 0)), "branding_watermark", "orange")
            metric_card("Departments", str(results.get("departments", 0)), "business", "orange")
            metric_card("Warnings", str(results.get("warnings", 0)), "warning", "orange" if results.get("warnings", 0) > 0 else "grey")
            metric_card("Errors", str(results.get("errors", 0)), "error", "red" if results.get("errors", 0) > 0 else "grey")
