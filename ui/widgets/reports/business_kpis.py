"""Business KPIs widget (Sprint 8)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_business_kpis(kpis: Dict[str, Any]) -> None:
    section_header("Business KPIs")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            stores = kpis.get("stores", {})
            metric_card("Stores", f"{stores.get('with_data', 0)}/{stores.get('total', 0)}", "store", "blue")
            upcs = kpis.get("upcs", {})
            metric_card("UPCs", f"{upcs.get('with_data', 0)}/{upcs.get('total', 0)}", "barcode", "blue")
            cats = kpis.get("categories", {})
            metric_card("Categories", f"{cats.get('with_data', 0)}/{cats.get('total', 0)}", "category", "blue")
            brands = kpis.get("brands", {})
            metric_card("Brands", f"{brands.get('with_data', 0)}/{brands.get('total', 0)}", "branding_watermark", "blue")
            depts = kpis.get("departments", {})
            metric_card("Departments", f"{depts.get('with_data', 0)}/{depts.get('total', 0)}", "layers", "blue")
            metric_card("Total Sales", f"${kpis.get('total_sales', 0):,.0f}", "payments", "green")
            metric_card("Total Quantity", f"{kpis.get('total_quantity', 0):,}", "inventory_2", "green")
            metric_card("Avg Basket", f"${kpis.get('average_basket', 0):.2f}", "shopping_cart", "green")
        dr = kpis.get("date_range", {})
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label(f"Date Range: {dr.get('from', '—')} → {dr.get('to', '—')}").classes("text-xs text-gray-500")
            gm = kpis.get("growth_metrics", {})
            ui.label(f"Sales QoQ: {gm.get('sales_qoq', 0):+.1f}%").classes("text-xs text-gray-500")
            ui.label(f"Qty QoQ: {gm.get('quantity_qoq', 0):+.1f}%").classes("text-xs text-gray-500")
