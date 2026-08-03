"""Diagnostic card widget (Sprint 9)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header


STATUS_COLORS = {"passed": "green", "failed": "red", "warning": "orange"}


def render_diagnostic_card(d: Dict[str, Any]) -> None:
    section_header("Diagnostics")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=2).classes("w-full gap-4"):
            for key in ["architecture", "contracts", "regression", "performance"]:
                item = d.get(key, {})
                status = item.get("status", "—")
                color = STATUS_COLORS.get(status, "gray")
                with ui.card().classes("p-3"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle" if status == "passed" else "cancel",
                                color=color, size="md")
                        ui.label(key.title()).classes("text-sm font-semibold")
                    ui.label(item.get("description", "")).classes("text-xs text-gray-500 mt-1")
                    ui.badge(status, color=color).props("outline")
        ver = d.get("version", {})
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label(f"App: {ver.get('app', '—')} | Backend: {ver.get('backend', '—')} | UI: {ver.get('ui', '—')}").classes("text-xs text-gray-500")
