"""Execution Planner workspace — Sprint 6A.

Reviews, configures, and approves execution plan.
"""

from nicegui import ui
from ui.widgets.cards import section_header, metric_card, empty_state
from ui.shared import op_svc, op_ctrl, navigate_to

from ui.widgets.operation.pipeline_viz import render_pipeline_viz
from ui.widgets.operation.execution_config import render_execution_config
from ui.widgets.operation.resource_estimation import render_resource_estimates
from ui.widgets.operation.readiness_checklist import render_readiness_checklist

from dav_platform.core.contracts import ExecutionStep


def render():
    ctrl = op_ctrl()

    # ── Execution Summary ────────────────────────────────────
    _render_execution_summary(ctrl.execution_summary)

    # ── Pipeline Visualization ───────────────────────────────
    render_pipeline_viz(ctrl.pipeline_stages)

    # ── Execution Steps ──────────────────────────────────────
    _render_execution_steps(ctrl.execution_steps)

    # ── Execution Configuration ─────────────────────────────
    render_execution_config(ctrl.config, ctrl.update_config)

    # ── Resource Estimates ───────────────────────────────────
    render_resource_estimates(ctrl.resource_estimates)

    # ── Expected Outputs ─────────────────────────────────────
    _render_expected_outputs(ctrl.expected_outputs)

    # ── Readiness ────────────────────────────────────────────
    render_readiness_checklist(ctrl.readiness_items, ctrl.overall_readiness)

    # ── Actions ──────────────────────────────────────────────
    _render_actions(ctrl)


def _render_execution_summary(summary: dict):
    section_header("Execution Summary")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Total Steps", str(summary.get("total_steps", "-")), "list", "blue")
            metric_card("Required Steps", str(summary.get("required_steps", "-")), "checklist", "green")
            metric_card("Layers", ", ".join(summary.get("layers", [])), "layers", "orange")
            metric_card("Mode", summary.get("mode", "-"), "play_circle", "primary")


def _render_execution_steps(steps: list):
    section_header("Execution Steps")
    if not steps:
        empty_state("No execution steps defined. Complete the Analysis Planner first.")
        return
    with ui.card().classes("w-full p-4"):
        for i, step in enumerate(steps):
            with ui.row().classes("items-center gap-3 py-2 border-b border-gray-100"):
                ui.badge(str(step.step_number), color="primary").classes("text-xs min-w-6")
                with ui.column().classes("flex-1 gap-0"):
                    ui.label(step.action).classes("text-sm font-semibold")
                    ui.label(step.description).classes("text-xs text-gray-500")
                if not step.required:
                    ui.badge("Optional", color="grey").classes("text-xs")
                ui.label(f"Layer: {step.layer}").classes("text-xs text-gray-400")


def _render_expected_outputs(outputs: list):
    section_header("Expected Outputs")
    with ui.card().classes("w-full p-4"):
        if outputs:
            with ui.grid(columns=3).classes("w-full gap-3"):
                for out in outputs:
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("description", color="blue").classes("text-lg")
                        ui.label(out).classes("text-sm")
        else:
            ui.label("No outputs defined").classes("text-sm text-gray-500")


def _render_actions(ctrl):
    ui.space().classes("h-4")
    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.button("Back to Planning", icon="arrow_back",
                      on_click=lambda: navigate_to("requirement")).props("flat")
            ui.button("Reset Config", icon="refresh",
                      on_click=ctrl.reset_config).props("flat")
            ui.button("Approve Plan", icon="check_circle",
                      on_click=ctrl.approve, color="positive").props(
                          "outline" if not ctrl.can_approve else "")
            ui.button("Continue to Execution", icon="arrow_forward", color="primary",
                      on_click=lambda: navigate_to("processing")).props("flat")

    if ctrl.is_approved:
        ui.badge("✓ Execution Plan Approved", color="green").classes("text-sm mt-2")
