"""Execution Center workspace — Sprint 6B.

Executes and monitors processing with live pipeline, progress,
logs, metrics, performance charts, and results.
"""

from nicegui import ui
from ui.widgets.cards import section_header, metric_card, empty_state
from ui.shared import proc_svc, proc_ctrl, navigate_to
from ui.widgets.guidance_bar import render_guidance

from ui.widgets.processing.live_pipeline import render_live_pipeline
from ui.widgets.processing.progress_panel import render_progress_panel
from ui.widgets.processing.log_viewer import render_log_viewer
from ui.widgets.processing.metrics_dashboard import render_metrics_dashboard
from ui.widgets.processing.performance_charts import render_performance_charts
from ui.widgets.processing.results_summary import render_results_summary


def render():
    render_guidance("processing")
    ctrl = proc_ctrl()

    _render_overview(ctrl)

    render_live_pipeline(ctrl.pipeline_stages)

    render_progress_panel(
        progress=ctrl.progress,
        stage_label=ctrl.current_stage_label,
        rows=ctrl.rows_processed,
        elapsed=ctrl.elapsed_seconds,
        rows_per_sec=ctrl.rows_per_sec,
    )

    render_log_viewer(ctrl.logs)

    render_metrics_dashboard(ctrl.metrics)

    render_performance_charts(ctrl.performance_data)

    if ctrl.is_completed:
        render_results_summary(ctrl.results_summary)


def _render_overview(ctrl):
    section_header("Execution Overview")
    with ui.card().classes("w-full p-4"):
        state = ctrl.state.value if ctrl.state else "pending"
        color_map = {"pending": "grey", "running": "blue", "completed": "green",
                     "failed": "red", "cancelled": "orange"}
        with ui.row().classes("items-center justify-between"):
            ui.label("Execution Status").classes("text-sm font-semibold")
            ui.badge(state.upper(), color=color_map.get(state, "grey")).classes("text-sm")
        ui.label(f"Processing State: {ctrl.current_stage_label}").classes("text-sm text-gray-500 mt-1")
