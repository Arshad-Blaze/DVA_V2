"""Business impact card widget (Sprint 7)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_business_impact(impact: Dict[str, Any]) -> None:
    section_header("Business Impact")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Critical", str(impact.get("critical", 0)), "priority_high",
                        "red" if impact.get("critical", 0) > 0 else "grey")
            metric_card("High", str(impact.get("high", 0)), "error", "red" if impact.get("high", 0) > 0 else "grey")
            metric_card("Medium", str(impact.get("medium", 0)), "warning", "orange")
            metric_card("Low", str(impact.get("low", 0)), "info", "blue")

        with ui.grid(columns=3).classes("w-full gap-4 mt-2"):
            metric_card("Business Readiness", impact.get("business_readiness", "-"), "business",
                        "green" if impact.get("business_readiness") == "Good" else "orange")
            metric_card("Affected Stores", str(impact.get("affected_stores", 0)), "store",
                        "red" if impact.get("affected_stores", 0) > 0 else "grey")
            metric_card("Risk Level", impact.get("risk_level", "-"), "gps_fixed",
                        "green" if impact.get("risk_level") == "Low" else "orange")

        with ui.grid(columns=2).classes("w-full gap-4 mt-2"):
            metric_card("Sales Impact", f"{impact.get('affected_sales_pct', 0):.1f}%", "payments",
                        "red" if impact.get("affected_sales_pct", 0) > 5 else "orange")
            metric_card("Quantity Impact", f"{impact.get('affected_quantity_pct', 0):.1f}%", "scale",
                        "red" if impact.get("affected_quantity_pct", 0) > 5 else "orange")
