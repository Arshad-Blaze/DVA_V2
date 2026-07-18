"""Validation score card widget (Sprint 7)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_validation_dashboard(d: Dict[str, Any]) -> None:
    section_header("Validation Dashboard")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label("Overall Quality").classes("text-sm font-semibold")
            color_map = {"High": "green", "Medium": "orange", "Low": "red"}
            ui.badge(d.get("overall_quality", "-"), color=color_map.get(d.get("overall_quality", ""), "grey")).classes("text-sm")

        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Total Rules", str(d.get("total_rules", 0)), "rule", "blue")
            metric_card("Passed", str(d.get("passed", 0)), "check_circle", "green")
            metric_card("Warnings", str(d.get("warnings", 0)), "warning", "orange")
            metric_card("Failed", str(d.get("failed", 0)), "error", "red")

        with ui.grid(columns=3).classes("w-full gap-4 mt-2"):
            metric_card("Critical", str(d.get("critical", 0)), "priority_high", "red" if d.get("critical", 0) > 0 else "grey")
            metric_card("Score", f"{d.get('score', 0):.0f}%", "percent", "green" if d.get("score", 80) >= 80 else "orange")
            metric_card("Business Readiness", d.get("business_readiness", "-"), "business", "green" if d.get("business_readiness") == "Good" else "orange")
