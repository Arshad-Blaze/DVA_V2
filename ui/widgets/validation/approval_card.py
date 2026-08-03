"""Approval card widget for Validation Center (Sprint 7)."""

from typing import Callable
from nicegui import ui
from ui.widgets.cards import section_header


def render_approval_card(
    is_approved: bool,
    is_rejected: bool,
    on_approve: Callable,
    on_reject: Callable,
    on_reset: Callable,
) -> None:
    section_header("Dataset Approval")
    with ui.card().classes("w-full p-4"):
        if is_approved:
            ui.badge("✓ Dataset Approved — Ready for Reports", color="green").classes("text-sm")
        elif is_rejected:
            ui.badge("✗ Dataset Rejected — Review Required", color="red").classes("text-sm")
        else:
            with ui.row().classes("gap-2"):
                ui.button("Approve Dataset", on_click=on_approve, icon="check", color="positive").props("outline")
                ui.button("Reject Dataset", on_click=on_reject, icon="close", color="red").props("outline")
                ui.button("Reset", on_click=on_reset, icon="refresh").props("flat")
