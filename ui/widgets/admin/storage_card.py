"""Storage card widget (Sprint 9)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_storage_card(s: Dict[str, Any]) -> None:
    section_header("Storage")
    with ui.card().classes("w-full p-4"):
        total = s.get("total_used_mb", 0) + s.get("total_available_mb", 0)
        pct = (s.get("total_used_mb", 0) / max(total, 1)) * 100
        with ui.row().classes("w-full items-center gap-4 mb-4"):
            ui.label(f"Used: {s.get('total_used_mb', 0):.1f} MB").classes("text-sm")
            with ui.progress(value=pct / 100, size="sm").props("rounded").classes("flex-1"):
                pass
            ui.label(f"Available: {s.get('total_available_mb', 0):.0f} MB").classes("text-sm text-gray-500")
        with ui.grid(columns=3).classes("w-full gap-2"):
            for key in ["projects", "reports", "cache", "logs", "exports", "temp"]:
                item = s.get(key, {})
                with ui.card().classes("p-2"):
                    ui.label(key.title()).classes("text-xs font-semibold text-gray-500")
                    ui.label(f"{item.get('size_mb', 0):.1f} MB ({item.get('count', 0)})").classes("text-sm")
