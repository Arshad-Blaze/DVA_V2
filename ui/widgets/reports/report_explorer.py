"""Report explorer widget (Sprint 8)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_report_explorer(
    explorer: Dict[str, Any],
    filtered_reports: List[Dict[str, Any]],
    selected_report: Optional[Dict[str, Any]],
    on_search: Callable,
    on_select_category: Callable,
    on_select_report: Callable,
) -> None:
    section_header("Report Explorer")
    with ui.card().classes("w-full p-4"):
        # Search
        ui.input("Search reports", placeholder="Search by name or type...",
                 on_change=lambda e: on_search(e.value)).props("outlined dense").classes("w-full mb-3")

        # Categories
        with ui.row().classes("gap-2 mb-3"):
            ui.button("All", on_click=lambda: on_select_category(None)).props("flat dense size=sm")
            for cat in explorer.get("categories", []):
                ui.button(cat["label"], on_click=lambda c=cat["id"]: on_select_category(c)).props("flat dense size=sm")

        # Pinned
        pinned = explorer.get("pinned", [])
        if pinned:
            ui.label("Pinned Reports").classes("text-sm font-semibold mt-2")
            with ui.grid(columns=3).classes("w-full gap-2 mb-3"):
                for p in pinned:
                    with ui.card().classes("p-2 cursor-pointer hover:shadow-md"):
                        ui.label(p["name"]).classes("text-sm font-medium")
                        ui.label(f"{p['type']} · {p['generated']}").classes("text-xs text-gray-500")

        # Filtered report list
        with ui.grid(columns=3).classes("w-full gap-2"):
            for r in filtered_reports:
                is_selected = selected_report and selected_report["id"] == r["id"]
                cls = "p-2 cursor-pointer border-2 " + ("border-blue-500" if is_selected else "border-transparent hover:border-gray-300")
                with ui.card().classes(cls).on("click", lambda rid=r["id"]: on_select_report(rid)):
                    ui.label(r["name"]).classes("text-sm font-medium")
                    ui.label(f"{r['type']} · {len(r['sections'])} sections").classes("text-xs text-gray-500")
