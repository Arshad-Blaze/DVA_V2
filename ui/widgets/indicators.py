"""Status indicator widgets."""

from nicegui import ui


def status_indicator(status: str = "idle") -> ui.html:
    colors = {"idle": "grey", "running": "blue", "success": "green", "failed": "red", "warning": "orange"}
    color = colors.get(status, "grey")
    return ui.html(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};"></span>')


def memory_indicator(usage_mb: float = 0, peak_mb: float = 0) -> ui.label:
    return ui.label(f"Mem: {usage_mb:.0f} MB").classes("text-xs text-gray-400")


def breadcrumb(items: list) -> ui.row:
    with ui.row().classes("items-center gap-1 text-sm text-gray-500") as row:
        for i, item in enumerate(items):
            ui.label(item)
            if i < len(items) - 1:
                ui.icon("chevron_right").classes("text-xs")
    return row
