"""Transformation quality dashboard widget."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_quality_dashboard(metrics: Dict[str, Any]) -> None:
    section_header("Transformation Quality")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=3).classes("w-full gap-4"):
            metric_card("Overall Quality", metrics.get("overall_quality", "-"), "verified", "green")
            metric_card("Mapping Confidence", f"{metrics.get('mapping_confidence', 0):.0%}", "trending_up", "blue")
            metric_card("Overall Readiness", metrics.get("overall_readiness", "-"), "flag", "orange" if "Review" in str(metrics.get("overall_readiness", "")) else "green")

        ui.separator().classes("my-3")

        with ui.grid(columns=3).classes("w-full gap-4"):
            metric_card("Required Coverage", metrics.get("required_coverage", "-"), "checklist", "green")
            metric_card("Optional Coverage", metrics.get("optional_coverage", "-"), "checklist", "blue")
            metric_card("Manual Mappings", str(metrics.get("manual_mappings", 0)), "edit", "orange")

        with ui.grid(columns=3).classes("w-full gap-4 mt-2"):
            metric_card("Auto Mappings", str(metrics.get("auto_mappings", 0)), "auto_fix_high", "blue")
            metric_card("Ignored Columns", str(metrics.get("ignored_columns", 0)), "visibility_off", "grey")
            metric_card("Missing Columns", str(metrics.get("missing_columns", 0)), "highlight_off", "red" if metrics.get("missing_columns", 0) > 0 else "grey")
