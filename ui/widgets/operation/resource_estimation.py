"""Resource estimation widget (Sprint 6A)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_resource_estimates(estimates: Dict[str, Any]) -> None:
    section_header("Estimated Resources")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Runtime", estimates.get("runtime", "-"), "timer", "blue")
            metric_card("Memory", estimates.get("memory", "-"), "memory", "green")
            metric_card("Peak Memory", estimates.get("peak_memory", "-"), "memory", "orange")
            metric_card("CPU", estimates.get("cpu", "-"), "memory", "blue")
        with ui.grid(columns=3).classes("w-full gap-4 mt-2"):
            streaming = estimates.get("streaming", False)
            metric_card("Streaming", "Enabled" if streaming else "Disabled", "cloud", "green" if streaming else "grey")
            metric_card("Rows", estimates.get("rows", "-"), "table_rows", "blue")
            metric_card("Output Size", estimates.get("output_size", "-"), "save_alt", "blue")
