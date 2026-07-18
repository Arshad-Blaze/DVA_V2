"""Export center widget (Sprint 8)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_export_center(
    formats: List[str],
    selected_format: str,
    selected_report: Optional[Dict[str, Any]],
    on_select_format: Callable,
    on_preview: Callable,
    on_export: Callable,
    on_export_all: Callable,
) -> None:
    section_header("Export Center")
    with ui.card().classes("w-full p-4"):
        # Format selector
        with ui.row().classes("gap-2 mb-3"):
            ui.label("Format: ").classes("text-sm font-medium")
            for fmt in formats:
                color = "primary" if fmt == selected_format else None
                ui.button(fmt.upper(), on_click=lambda f=fmt: on_select_format(f)).props(f"flat dense{' color=primary' if color else ''}")

        # Preview
        ui.label("Preview:").classes("text-sm font-semibold mt-2 mb-1")
        preview = ui.textarea().props("outlined dense readonly").classes("w-full text-xs font-mono")
        preview.value = on_preview() if hasattr(on_preview, '__call__') else ""

        # Export actions
        with ui.row().classes("gap-2 mt-3"):
            ui.button("Export Selected", icon="download", color="primary",
                      on_click=lambda: _do_export(on_export, selected_report)).props("flat")
            ui.button("Export All", icon="download", color="primary",
                      on_click=lambda: _do_export_all(on_export_all)).props("flat")


def _do_export(on_export: Callable, selected: Optional[Dict[str, Any]]) -> None:
    if not selected:
        return
    on_export()


def _do_export_all(on_export_all: Callable) -> None:
    on_export_all()
