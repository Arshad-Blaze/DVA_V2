"""Approval panel widget."""

from typing import Any, Callable, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_approval_panel(
    checklist: List[Dict[str, Any]],
    can_approve: bool,
    is_approved: bool,
    is_rejected: bool,
    on_approve: Callable,
    on_reject: Callable,
    on_back: Callable,
) -> None:
    section_header("Approval Panel")
    with ui.card().classes("w-full p-4"):
        ui.label("Pre-Processing Checklist").classes("text-sm font-semibold mb-3")

        with ui.column().classes("w-full gap-2 mb-4"):
            for c in checklist:
                icon = "check_circle" if c["status"] else "radio_button_unchecked"
                color = "green" if c["status"] else "grey"
                with ui.row().classes("items-center gap-2"):
                    ui.icon(icon, color=color).classes("text-lg")
                    ui.label(c["label"]).classes("text-sm")

        if is_approved:
            ui.badge("✓ Approved", color="green").classes("text-sm")
        elif is_rejected:
            ui.badge("✗ Rejected — Review Required", color="red").classes("text-sm")
        else:
            with ui.row().classes("gap-2"):
                ui.button("Approve", on_click=on_approve, icon="check").props(
                    "disabled flat" if not can_approve else "outline"
                ).classes("text-sm")
                ui.button("Reject", on_click=on_reject, icon="close", color="red").props("flat").classes("text-sm")
                ui.button("Back to Mapping", on_click=on_back, icon="arrow_back").props("flat").classes("text-sm")
