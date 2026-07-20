"""Administration, History & Diagnostics Center — Sprint 9.

System health, project/execution history, log viewer, diagnostics,
storage, settings, maintenance, about, and actions.
"""

from nicegui import ui
from ui.shared import admin_ctrl, navigate_to
from ui.widgets.guidance_bar import render_guidance
from ui.widgets.admin.health_card import render_health_card
from ui.widgets.admin.history_grid import render_project_history, render_execution_history
from ui.widgets.admin.log_viewer import render_log_viewer
from ui.widgets.admin.diagnostic_card import render_diagnostic_card
from ui.widgets.admin.storage_card import render_storage_card
from ui.widgets.admin.settings_panel import render_settings_panel
from ui.widgets.admin.maintenance_card import render_maintenance_card
from ui.widgets.admin.about_section import render_about_section
from ui.widgets.admin.status_bar import render_admin_status_bar


def render():
    render_guidance("administration")
    ctrl = admin_ctrl()

    # ── Status Bar ───────────────────────────────────────────
    render_admin_status_bar(ctrl.status_bar)

    # ── System Health ────────────────────────────────────────
    render_health_card(ctrl.system_health)

    # ── Project History ──────────────────────────────────────
    render_project_history(
        projects=ctrl.project_history,
        selected=ctrl.selected_project,
        on_select=ctrl.select_project,
    )

    # ── Execution History ────────────────────────────────────
    render_execution_history(
        executions=ctrl.execution_history,
        selected=ctrl.selected_execution,
        on_select=ctrl.select_execution,
    )

    # ── Log Viewer ───────────────────────────────────────────
    render_log_viewer(
        logs=ctrl.filtered_logs,
        selected=ctrl.selected_log,
        log_sources=ctrl.log_sources,
        on_search=ctrl.set_log_search,
        on_filter_severity=ctrl.set_log_severity,
        on_filter_source=ctrl.set_log_source,
        on_select=ctrl.select_log,
        on_export=ctrl.export_logs,
    )

    # ── Diagnostics ──────────────────────────────────────────
    render_diagnostic_card(ctrl.diagnostics)

    # ── Storage ──────────────────────────────────────────────
    render_storage_card(ctrl.storage)

    # ── Settings ─────────────────────────────────────────────
    render_settings_panel(
        settings=ctrl.settings,
        defaults=ctrl.default_settings,
        on_update=ctrl.update_setting,
        on_reset=ctrl.reset_settings,
    )

    # ── Maintenance ──────────────────────────────────────────
    render_maintenance_card(
        actions=ctrl.maintenance_actions,
        on_run=ctrl.run_maintenance,
    )

    # ── About ────────────────────────────────────────────────
    render_about_section(ctrl.about)

    # ── Actions ──────────────────────────────────────────────
    _render_actions(ctrl)


def _render_actions(ctrl):
    ui.space().classes("h-4")
    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.button("Export Logs", icon="download",
                      on_click=ctrl.export_logs).props("flat")
            ui.button("Reset Settings", icon="restart_alt",
                      on_click=ctrl.reset_settings).props("flat")
            ui.button("Back to Reports", icon="arrow_back",
                      on_click=lambda: navigate_to("reports")).props("flat")
