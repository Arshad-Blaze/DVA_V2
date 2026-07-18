"""Rule detail viewer widget (Sprint 7)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_rule_viewer(
    rules: List[Dict[str, Any]],
    selected: Optional[Dict[str, Any]],
    on_select: Callable,
) -> None:
    section_header("Rule Details")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-2"):
            ui.label("Select a rule to inspect").classes("text-sm text-gray-500")
            with ui.row().classes("gap-1"):
                for r in rules:
                    is_sel = selected and r["name"] == selected["name"]
                    ui.button(r["name"][:15] + ("..." if len(r["name"]) > 15 else ""),
                              on_click=lambda n=r["name"]: on_select(n),
                              color="primary" if is_sel else "grey").props("flat dense").classes("text-xs")

        if selected:
            ui.separator().classes("my-2")
            with ui.grid(columns=2).classes("w-full gap-4"):
                with ui.column().classes("gap-2"):
                    _detail_item("Rule", selected.get("name", ""))
                    _detail_item("Type", selected.get("rule_type", ""))
                    _detail_item("Severity", selected.get("severity", ""))
                    _detail_item("Columns", ", ".join(selected.get("columns", [])))
                with ui.column().classes("gap-2"):
                    _detail_item("Affected Rows", str(selected.get("affected_rows", 0)))
                    _detail_item("Affected Stores", str(selected.get("affected_stores", 0)))
                    _detail_item("Affected UPCs", str(selected.get("affected_upcs", 0)))

            ui.separator().classes("my-2")
            ui.label(selected.get("description", "")).classes("text-sm text-gray-700")
            ui.label(f"Business: {selected.get('business_meaning', '')}").classes("text-xs text-gray-500 mt-1")
            ui.label(f"Example: {selected.get('examples', '')}").classes("text-xs text-gray-500 mt-1")
            ui.label(f"Resolution: {selected.get('resolution', '')}").classes("text-xs text-blue-500 mt-1")


def _detail_item(label: str, value: str) -> None:
    with ui.row().classes("items-center gap-2"):
        ui.label(label + ":").classes("text-xs text-gray-500 min-w-24")
        ui.label(value).classes("text-xs font-semibold")
