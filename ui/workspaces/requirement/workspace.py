"""Analysis Planner workspace — Sprint 5.

Business goal selection, recommendation, capability matrix,
execution plan, readiness dashboard, and confirmation.
"""

from nicegui import ui
from ui.widgets.cards import section_header, empty_state
from ui.shared import req_ctrl, navigate_to
from ui.widgets.guidance_bar import render_guidance

from ui.widgets.requirement.goal_card import render_goal_selection
from ui.widgets.requirement.recommendation_card import render_recommendation
from ui.widgets.requirement.capability_matrix import render_capability_matrix
from ui.widgets.requirement.execution_timeline import render_execution_timeline
from ui.widgets.requirement.readiness_gauge import render_readiness_gauge
from ui.widgets.requirement.output_preview_card import render_output_preview
from ui.widgets.requirement.warning_banner import render_warnings


def render():
    render_guidance("requirement")
    ctrl = req_ctrl()

    # ── Goal Selection ───────────────────────────────────────
    render_goal_selection(
        goals=ctrl.available_goals,
        selected_id=ctrl.selected_goal_id,
        on_select=ctrl.select_goal,
    )

    if ctrl.selected_goal_id is None:
        _render_no_selection()
        return

    # ── Recommendation ───────────────────────────────────────
    render_recommendation(
        recommendation=ctrl.recommendation,
        accepted=ctrl.recommendation_accepted,
        on_accept=ctrl.accept_recommendation,
        on_change_goal=ctrl.clear_goal,
    )

    # ── Capability Matrix ────────────────────────────────────
    render_capability_matrix(
        matrix=ctrl.capability_matrix,
        descriptions=ctrl.capability_descriptions,
    )

    # ── Missing Inputs ───────────────────────────────────────
    _render_missing_inputs(ctrl.missing_inputs)

    # ── Execution Plan ───────────────────────────────────────
    render_execution_timeline(steps=ctrl.execution_plan)

    # ── Expected Outputs & Estimates ─────────────────────────
    render_output_preview(
        outputs=ctrl.expected_outputs,
        estimates=ctrl.execution_estimates,
    )

    # ── Warnings ─────────────────────────────────────────────
    render_warnings(ctrl.warnings)

    # ── Readiness Dashboard ──────────────────────────────────
    render_readiness_gauge(
        readiness=ctrl.readiness,
        overall=ctrl.overall_readiness,
    )

    # ── Actions ──────────────────────────────────────────────
    _render_actions(ctrl)


def _render_no_selection():
    empty_state(
        message="Select a business goal above to generate your analysis plan",
        icon="lightbulb",
    )
    with ui.row().classes("w-full justify-center mt-4"):
        ui.button("Back to Business Preview", icon="arrow_back",
                  on_click=lambda: navigate_to("preview")).props("flat")


def _render_missing_inputs(missing: list):
    if not missing:
        return
    section_header("Missing Inputs")
    with ui.card().classes("w-full p-4 border-l-4 border-orange-400"):
        for m in missing:
            with ui.row().classes("items-center gap-3 py-2"):
                ui.icon("error_outline", color="orange").classes("text-lg")
                with ui.column().classes("gap-0 flex-1"):
                    ui.label(m.get("input", "")).classes("text-sm font-semibold")
                    ui.label(m.get("detail", "")).classes("text-xs text-gray-500")
                nav = m.get("navigate", "")
                if nav:
                    ui.button("Go", icon="arrow_forward", color="orange",
                              on_click=lambda w=nav: navigate_to(w)).props("flat dense")


def _render_actions(ctrl):
    ui.space().classes("h-4")
    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.button("Back to Preview", icon="arrow_back",
                      on_click=lambda: navigate_to("preview")).props("flat")
            ui.button("Generate Plan", icon="auto_fix_high",
                      on_click=ctrl.accept_recommendation,
                      color="primary").props("outline")
            ui.button("Confirm Plan", icon="check",
                      on_click=ctrl.confirm_plan,
                      color="positive").props(
                          "outline" if not ctrl.can_confirm else ""
                      )
            ui.button("Reset", icon="refresh",
                      on_click=ctrl.reset).props("flat")

    if ctrl.is_confirmed:
        ui.badge("✓ Plan Confirmed — Ready for Execution", color="green").classes("text-sm mt-2")
    elif ctrl.selected_goal_id and not ctrl.recommendation_accepted:
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.icon("info", color="blue").classes("text-sm")
            ui.label("Accept the recommendation to proceed with confirmation").classes("text-sm text-blue-500")
