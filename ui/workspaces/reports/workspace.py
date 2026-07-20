"""Reports & Insights Center — Sprint 8.

Executive dashboard with KPIs, report explorer, interactive reports,
charts, drill down, export center, and report history.
"""

from nicegui import ui
from ui.shared import reports_ctrl, navigate_to
from ui.widgets.guidance_bar import render_guidance
from ui.widgets.reports.executive_dashboard import render_executive_dashboard
from ui.widgets.reports.business_kpis import render_business_kpis
from ui.widgets.reports.validation_kpis import render_validation_kpis
from ui.widgets.reports.report_explorer import render_report_explorer
from ui.widgets.reports.report_viewer import render_report_viewer
from ui.widgets.reports.chart_card import render_chart_card
from ui.widgets.reports.drill_down import render_drill_down
from ui.widgets.reports.export_center import render_export_center
from ui.widgets.reports.report_history import render_report_history
from ui.widgets.reports.status_bar import render_status_bar


def render():
    render_guidance("reports")
    ctrl = reports_ctrl()

    # ── Executive Dashboard ──────────────────────────────────
    render_executive_dashboard(ctrl.executive_dashboard)

    # ── Business KPIs ────────────────────────────────────────
    render_business_kpis(ctrl.business_kpis)

    # ── Validation KPIs ──────────────────────────────────────
    render_validation_kpis(ctrl.validation_kpis)

    # ── Report Explorer ──────────────────────────────────────
    render_report_explorer(
        explorer=ctrl.report_explorer,
        filtered_reports=ctrl.filtered_reports,
        selected_report=ctrl.selected_report,
        on_search=ctrl.set_search_query,
        on_select_category=ctrl.select_category,
        on_select_report=ctrl.select_report,
    )

    # ── Interactive Reports ──────────────────────────────────
    render_report_viewer(
        reports=ctrl.all_reports,
        selected=ctrl.selected_report,
    )

    # ── Charts ───────────────────────────────────────────────
    render_chart_card(
        chart_keys=ctrl.chart_keys,
        selected=ctrl.selected_chart,
        selected_key=ctrl.selected_chart_key,
        on_select=ctrl.select_chart,
    )

    # ── Drill Down ───────────────────────────────────────────
    render_drill_down(
        level=ctrl.drill_down_level,
        level_id=ctrl.drill_down_id,
        data=ctrl.drill_down_data,
        on_drill_store=ctrl.drill_to_store,
        on_drill_upc=ctrl.drill_to_upc,
        on_drill_validation=ctrl.drill_to_validation,
        on_drill_business=ctrl.drill_to_business,
        on_drill_up=ctrl.drill_up,
        on_drill_reset=ctrl.drill_reset,
    )

    # ── Export Center ────────────────────────────────────────
    render_export_center(
        formats=ctrl.export_formats,
        selected_format=ctrl.selected_format,
        selected_report=ctrl.selected_report,
        on_select_format=ctrl.select_format,
        on_preview=ctrl.preview_export,
        on_export=ctrl.export_report,
        on_export_all=ctrl.export_all,
    )

    # ── Report History ───────────────────────────────────────
    render_report_history(ctrl.report_history)

    # ── Actions ──────────────────────────────────────────────
    _render_actions(ctrl)


def _render_actions(ctrl):
    ui.space().classes("h-4")
    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.button("Export Selected", icon="download", color="primary",
                      on_click=ctrl.export_report).props("flat")
            ui.button("Export All", icon="download",
                      on_click=ctrl.export_all).props("flat")
            ui.button("Back to Validation", icon="arrow_back",
                      on_click=lambda: navigate_to("validation")).props("flat")
