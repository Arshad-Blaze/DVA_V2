"""Admin status bar widget (Sprint 9)."""

from typing import Any, Dict
from nicegui import ui


def render_admin_status_bar(status: Dict[str, Any]) -> None:
    with ui.card().classes("w-full p-2 bg-gray-50"):
        with ui.row().classes("w-full items-center justify-between text-xs text-gray-500"):
            health = status.get("health", "—")
            color = "green" if health == "healthy" else "orange"
            ui.label("Health: ").classes("font-medium")
            ui.badge(health, color=color).props("outline")
            ui.label(f"Memory: {status.get('memory', '—')}")
            ui.label(f"Version: {status.get('version', '—')}")
