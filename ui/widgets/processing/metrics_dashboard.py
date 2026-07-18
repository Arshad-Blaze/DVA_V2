"""Metrics dashboard widget (Sprint 6B)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_metrics_dashboard(metrics: Dict[str, Any]) -> None:
    section_header("Metrics")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Memory", f'{metrics.get("memory_mb", 0):.0f} MB', "memory", "blue")
            metric_card("Peak Memory", f'{metrics.get("peak_memory_mb", 0):.0f} MB', "memory", "orange")
            metric_card("CPU", f'{metrics.get("cpu_pct", 0):.0f}%', "memory", "green")
            metric_card("Streaming", "Active" if metrics.get("streaming") else "Inactive", "cloud", "blue")
        with ui.grid(columns=4).classes("w-full gap-4 mt-2"):
            metric_card("Chunks", str(metrics.get("chunks", 0)), "grid_view", "purple")
            metric_card("Rows", f'{metrics.get("rows", 0):,}', "table_rows", "blue")
            metric_card("Aggregations", "Enabled" if metrics.get("aggregations") else "Pending", "functions", "green")
            metric_card("Calculations", "Enabled" if metrics.get("calculations") else "Pending", "calculate", "green")
