"""Validation KPIs widget (Sprint 8)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_validation_kpis(kpis: Dict[str, Any]) -> None:
    section_header("Validation KPIs")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Passed", f"{kpis.get('passed_rules', 0)}/{kpis.get('total_rules', 0)}", "check_circle", "green")
            metric_card("Failed", str(kpis.get('failed_rules', 0)), "cancel", "red")
            metric_card("Warnings", str(kpis.get('warnings', 0)), "warning", "orange")
            metric_card("Critical", str(kpis.get('critical', 0)), "error", "red" if kpis.get('critical', 0) > 0 else "green")
            metric_card("Store Success", f"{kpis.get('store_success_pct', 0):.0f}%", "store", "blue")
            metric_card("UPC Success", f"{kpis.get('upc_success_pct', 0):.0f}%", "barcode", "blue")
            metric_card("Coverage", f"{kpis.get('coverage_pct', 0):.0f}%", "pie_chart", "blue")
