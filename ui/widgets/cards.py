"""Reusable card widgets."""

from typing import Optional

from nicegui import ui


def info_card(title: str, description: str = "", icon: str = "info", color: str = "primary") -> ui.card:
    with ui.card().classes("workspace-card w-full") as card:
        with ui.row().classes("items-center gap-3"):
            ui.icon(icon, color=color).classes("text-2xl")
            ui.label(title).classes("text-lg font-semibold")
        if description:
            ui.label(description).classes("text-sm text-gray-500 mt-1")
    return card


def metric_card(label: str, value: str, icon: str = "", color: str = "primary") -> ui.card:
    with ui.card().classes("metric-card") as card:
        if icon:
            ui.icon(icon, color=color).classes("text-xl")
        ui.label(value).classes("metric-value")
        ui.label(label).classes("metric-label")
    return card


def section_header(title: str) -> ui.label:
    return ui.label(title).classes("section-header w-full")


def status_badge(text: str, status: str = "info") -> ui.html:
    return ui.html(f'<span class="status-badge {status}">{text}</span>')


def workspace_card(title: str, description: str = "", icon: str = "tab",
                   disabled: bool = False, active: bool = False,
                   on_click: Optional[callable] = None) -> ui.card:
    with ui.card().classes("workspace-card cursor-pointer").props("clickable") as card:
        with ui.row().classes("items-center gap-3"):
            ui.icon(icon).classes("text-2xl")
            with ui.column().classes("gap-0"):
                ui.label(title).classes("font-semibold")
                if description:
                    ui.label(description).classes("text-xs text-gray-500")
        if on_click:
            card.on("click", on_click)
    if disabled:
        card.classes("opacity-50 pointer-events-none")
    if active:
        card.classes("border-accent")
    return card


def empty_state(message: str = "No data available", icon: str = "inbox") -> ui.column:
    with ui.column().classes("empty-state") as col:
        ui.icon(icon, color="grey").classes("text-5xl")
        ui.label(message).classes("text-lg")
    return col


def loading_state(message: str = "Loading...") -> ui.row:
    with ui.row().classes("loading-state") as row:
        ui.spinner(color="primary", size="2em")
        ui.label(message).classes("ml-3")
    return row
