"""Reusable guidance bar widget for workspace guidance."""
from nicegui import ui
from ui import shared


def render_guidance(workspace_id: str) -> None:
    guidance_svc = shared.guidance_svc()
    guidance = guidance_svc.get_guidance(workspace_id)
    if not guidance:
        return
    
    with ui.card().classes("w-full p-4 mb-4 bg-blue-50 border border-blue-200"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("help_outline").classes("text-blue-500")
                ui.label(f"Step: {guidance['step']}").classes("font-semibold text-sm text-blue-800")
            if guidance["estimated_time"] != "N/A":
                ui.label(f"~{guidance['estimated_time']}").classes("text-xs text-blue-500")
        
        ui.label(guidance["purpose"]).classes("text-sm text-gray-700 mt-1")
        ui.label(guidance["instructions"]).classes("text-sm text-gray-600 mt-1")
        
        with ui.expansion("Show details", icon="info").classes("w-full mt-1"):
            if guidance["required_inputs"]:
                ui.label("Required Inputs:").classes("text-xs font-semibold mt-1")
                for inp in guidance["required_inputs"]:
                    ui.label(f"  {inp}").classes("text-xs text-gray-500")
            if guidance["expected_outputs"]:
                ui.label("Expected Outputs:").classes("text-xs font-semibold mt-1")
                for out in guidance["expected_outputs"]:
                    ui.label(f"  {out}").classes("text-xs text-gray-500")
        
        with ui.row().classes("w-full justify-between items-center mt-2"):
            if guidance["progress"] > 0:
                ui.linear_progress(value=guidance["progress"] / 100, size="8px")
            else:
                ui.label("")
            next_step = guidance["next_step"]
            if next_step:
                next_label = next_step.replace("_", " ").title()
                ui.button(f"Next: {next_label}", icon="arrow_forward",
                         on_click=lambda ns=next_step: shared.navigate_to(ns)).props("flat color=primary size=sm")
