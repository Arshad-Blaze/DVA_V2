"""Drill-down widget (Sprint 8)."""

from typing import Any, Callable, Dict, Optional
from nicegui import ui
from ui.widgets.cards import section_header


HIERARCHY_LABELS = {
    "dashboard": "Dashboard",
    "store": "Store",
    "upc": "UPC",
    "validation": "Validation",
    "business": "Business Details",
}


def render_drill_down(
    level: str,
    level_id: Optional[str],
    data: Dict[str, Any],
    on_drill_store: Callable,
    on_drill_upc: Callable,
    on_drill_validation: Callable,
    on_drill_business: Callable,
    on_drill_up: Callable,
    on_drill_reset: Callable,
) -> None:
    section_header("Drill Down")
    with ui.card().classes("w-full p-4"):
        # Breadcrumb
        level_names = ["dashboard", "store", "upc", "validation", "business"]
        current_idx = level_names.index(level) if level in level_names else -1
        with ui.row().classes("items-center gap-1 mb-3"):
            for i, lvl in enumerate(level_names):
                if i > 0:
                    ui.icon("chevron_right", size="sm").classes("text-gray-400")
                is_current = i == current_idx
                cls = "text-sm font-medium" + (" text-blue-600" if is_current else " text-gray-500")
                ui.label(HIERARCHY_LABELS[lvl]).classes(cls)
                if is_current:
                    break

        # Content per level
        if level == "dashboard":
            stores = data.get("stores", [])
            with ui.grid(columns=3).classes("w-full gap-2"):
                for s in stores:
                    with ui.card().classes("p-2 cursor-pointer hover:shadow-md").on("click", lambda sid=s["id"]: on_drill_store(sid)):
                        ui.label(s["id"]).classes("text-sm font-medium")
                        ui.label(f"Sales: ${s['sales']:,}").classes("text-xs text-gray-500")
                        ui.label(f"Validation: {s['validation']}").classes("text-xs " + (
                            "text-green-600" if s['validation'] == 'pass' else "text-orange-600" if s['validation'] == 'warn' else "text-red-600"
                        ))

        elif level == "store":
            store = next((s for s in data.get("stores", []) if s["id"] == level_id), None)
            if store:
                with ui.card().classes("w-full p-3 bg-gray-50"):
                    ui.label(f"{store['id']} — {store.get('name', '')}").classes("text-base font-semibold")
                    with ui.grid(columns=3).classes("w-full gap-2 mt-2"):
                        metric("Sales", f"${store['sales']:,}")
                        metric("Quantity", f"{store['quantity']:,}")
                        metric("UPCs", str(store['upcs']))
                    with ui.row().classes("gap-2 mt-3"):
                        ui.button("View UPCs", on_click=lambda: on_drill_upc(store["id"])).props("flat dense")
                        ui.button("Validate", on_click=on_drill_validation).props("flat dense")
                        ui.button("Business", on_click=on_drill_business).props("flat dense")
            else:
                ui.label(f"Store {level_id} not found.").classes("text-sm text-gray-500")

        elif level == "upc":
            upcs = data.get("upcs", [])
            with ui.grid(columns=3).classes("w-full gap-2"):
                for u in upcs:
                    with ui.card().classes("p-2"):
                        ui.label(u["id"]).classes("text-sm font-medium")
                        ui.label(f"Sales: ${u['sales']:,}").classes("text-xs text-gray-500")

        elif level == "validation":
            ui.label("Validation drill-down: view rule results per entity.").classes("text-sm text-gray-500")
            with ui.row().classes("gap-2 mt-2"):
                ui.button("Back to Store", on_click=on_drill_up).props("flat dense")
                ui.button("Business Impact", on_click=on_drill_business).props("flat dense")

        elif level == "business":
            ui.label("Business details drill-down: KPIs and metrics per entity.").classes("text-sm text-gray-500")
            with ui.row().classes("gap-2 mt-2"):
                ui.button("Back", on_click=on_drill_up).props("flat dense")

        # Navigation actions
        with ui.row().classes("gap-2 mt-3 justify-between"):
            if level != "dashboard":
                ui.button("⬆ Drill Up", on_click=on_drill_up).props("flat dense")
            ui.button("↺ Reset", on_click=on_drill_reset).props("flat dense")


def metric(label: str, value: str) -> None:
    with ui.column().classes("items-center"):
        ui.label(value).classes("text-lg font-bold")
        ui.label(label).classes("text-xs text-gray-500")
