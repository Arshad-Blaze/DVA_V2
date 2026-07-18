"""Status bar widget (Sprint 8)."""

from typing import Any, Dict
from nicegui import ui


def render_status_bar(status: Dict[str, Any]) -> None:
    with ui.card().classes("w-full p-2 bg-gray-50"):
        with ui.row().classes("w-full items-center justify-between text-xs text-gray-500"):
            ui.label(f"Reports: {status.get('report_count', 0)}")
            current = status.get("current_report")
            ui.label(f"Current: {current}" if current else "Current: —")
            ui.label(f"Dataset: {status.get('dataset', '—')}")
            ui.label(f"Export: {status.get('export_status', '—')}")
