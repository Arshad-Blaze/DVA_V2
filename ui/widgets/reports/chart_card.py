"""Chart card widget (Sprint 8)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


CHART_LABELS = {
    "sales_by_store": "Sales by Store",
    "sales_by_category": "Sales by Category",
    "quantity_by_store": "Quantity by Store",
    "validation_distribution": "Validation Distribution",
    "rule_severity": "Rule Severity",
    "business_completeness": "Business Completeness",
}


def render_chart_card(
    chart_keys: List[str],
    selected: Optional[Dict[str, Any]],
    selected_key: Optional[str],
    on_select: Callable,
) -> None:
    section_header("Charts")
    with ui.card().classes("w-full p-4"):
        # Chart selector
        with ui.row().classes("gap-2 mb-3"):
            for key in chart_keys:
                label = CHART_LABELS.get(key, key.replace("_", " ").title())
                is_active = key == selected_key
                color = "primary" if is_active else None
                ui.button(label, on_click=lambda k=key: on_select(k)).props(f"flat dense size=sm{' color=primary' if is_active else ''}")

        if selected:
            labels = selected.get("labels", [])
            values = selected.get("values", [])
            max_val = max(values) if values else 1
            with ui.card().classes("w-full p-3 bg-gray-50"):
                ui.label(CHART_LABELS.get(selected_key or "", "Chart")).classes("text-sm font-semibold mb-2")
                for i, label in enumerate(labels):
                    pct = (values[i] / max_val * 100) if max_val else 0
                    with ui.row().classes("items-center gap-2 w-full"):
                        ui.label(label).classes("text-xs w-24")
                        with ui.progress(value=pct / 100, size="sm").props("rounded").classes("flex-1"):
                            pass
                        ui.label(str(values[i])).classes("text-xs text-gray-500 w-16 text-right")
        else:
            ui.label("Select a chart to view.").classes("text-sm text-gray-500")
