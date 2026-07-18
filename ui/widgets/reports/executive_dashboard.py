"""Executive dashboard widget (Sprint 8)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_executive_dashboard(d: Dict[str, Any]) -> None:
    section_header("Executive Dashboard")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card(
                "Overall Health", d.get("overall_health", "—"),
                "monitor_heart", "green" if d.get("overall_health") == "Good" else "orange",
            )
            metric_card(
                "Validation Score", f"{d.get('validation_score', 0):.0f}%",
                "score", "blue",
            )
            metric_card(
                "Business Readiness", d.get("business_readiness", "—"),
                "business", "green" if d.get("business_readiness") == "Good" else "orange",
            )
            metric_card(
                "Runtime", d.get("execution_runtime", "—"),
                "timer", "orange",
            )
            metric_card(
                "Reports", str(d.get("reports_generated", 0)),
                "assessment", "blue",
            )
            metric_card(
                "Critical Issues", str(d.get("critical_issues", 0)),
                "error", "red" if d.get("critical_issues", 0) > 0 else "green",
            )
            metric_card(
                "Warnings", str(d.get("warnings", 0)),
                "warning", "orange" if d.get("warnings", 0) > 0 else "green",
            )
            streaming = d.get("streaming", False)
            metric_card(
                "Streaming", "Enabled" if streaming else "Disabled",
                "stream", "green" if streaming else "gray",
            )
