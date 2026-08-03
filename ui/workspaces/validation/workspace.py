"""Validation Center workspace — Sprint 7.

Quality control dashboard with heat map, issue explorer,
expected vs actual comparison, rule details, business impact,
suggested actions, timeline, and approval workflow.
"""

from nicegui import ui
from ui.shared import val_ctrl, navigate_to
from ui.widgets.guidance_bar import render_guidance

from ui.widgets.validation.execution_summary import render_execution_summary
from ui.widgets.validation.score_card import render_validation_dashboard
from ui.widgets.validation.heat_map import render_heat_map
from ui.widgets.validation.issue_table import render_issue_table
from ui.widgets.validation.comparison_viewer import render_comparison
from ui.widgets.validation.rule_viewer import render_rule_viewer
from ui.widgets.validation.impact_card import render_business_impact
from ui.widgets.validation.timeline_widget import render_timeline
from ui.widgets.validation.recommendation_panel import render_recommendations
from ui.widgets.validation.approval_card import render_approval_card


def render():
    render_guidance("validation")
    ctrl = val_ctrl()

    # ── Execution Summary ────────────────────────────────────
    render_execution_summary()

    # ── Validation Dashboard ─────────────────────────────────
    render_validation_dashboard(ctrl.dashboard)

    # ── Validation Heat Map ──────────────────────────────────
    render_heat_map(
        rows=ctrl.heat_map_rows,
        columns=ctrl.heat_map_columns,
        data=ctrl.heat_map_data,
        on_cell_click=lambda r, c: None,
    )

    # ── Issue Explorer ───────────────────────────────────────
    render_issue_table(
        issues=ctrl.filtered_issues,
        total_count=ctrl.issue_count,
        on_search=ctrl.set_search_query,
        on_filter=ctrl.set_severity_filter,
        on_select=ctrl.select_issue,
    )

    # ── Expected vs Actual ───────────────────────────────────
    render_comparison(ctrl.comparison_data)

    # ── Rule Details ─────────────────────────────────────────
    render_rule_viewer(
        rules=ctrl.all_rules,
        selected=ctrl.selected_rule,
        on_select=ctrl.select_rule,
    )

    # ── Business Impact ──────────────────────────────────────
    render_business_impact(ctrl.business_impact)

    # ── Suggested Actions ────────────────────────────────────
    render_recommendations(
        actions=ctrl.suggested_actions,
        on_navigate=navigate_to,
    )

    # ── Timeline ─────────────────────────────────────────────
    render_timeline(ctrl.timeline_stages)

    # ── Approval ─────────────────────────────────────────────
    render_approval_card(
        is_approved=ctrl.is_approved,
        is_rejected=ctrl.is_rejected,
        on_approve=ctrl.approve,
        on_reject=ctrl.reject,
        on_reset=ctrl.reset,
    )

    # ── Actions ──────────────────────────────────────────────
    _render_actions(ctrl)


def _render_actions(ctrl):
    ui.space().classes("h-4")
    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.button("Export Report", icon="download",
                      on_click=ctrl.export_report).props("flat")
            ui.button("Export Failed", icon="download",
                      on_click=ctrl.export_failed).props("flat")
            ui.button("Back to Execution", icon="arrow_back",
                      on_click=lambda: navigate_to("processing")).props("flat")
            ui.button("Continue to Reports", icon="arrow_forward", color="primary",
                      on_click=lambda: navigate_to("reports")).props("flat")
