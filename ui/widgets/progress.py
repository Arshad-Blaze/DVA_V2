"""Progress indicator widgets."""

from nicegui import ui


def spinner(message: str = "Processing...", size: str = "2em") -> ui.row:
    with ui.row().classes("items-center justify-center p-8") as row:
        ui.spinner(color="primary", size=size)
        ui.label(message).classes("ml-3 text-gray-500")
    return row


def progress_bar(value: float = 0.0, label: str = "", show_percentage: bool = True) -> ui.row:
    with ui.row().classes("w-full items-center gap-3") as row:
        if label:
            ui.label(label).classes("text-sm min-w-24")
        ui.linear_progress(value=value, size="20px").classes("flex-1")
        if show_percentage:
            ui.label(f"{value * 100:.0f}%").classes("text-xs font-mono min-w-10")
    return row


def step_progress(steps: list, current_step: int = 0) -> ui.row:
    with ui.row().classes("w-full items-center gap-2 py-2") as row:
        for i, step in enumerate(steps):
            is_active = i == current_step
            is_done = i < current_step
            color = "positive" if is_done else ("primary" if is_active else "grey")
            icon = "check_circle" if is_done else ("circle" if is_active else "radio_button_unchecked")
            with ui.row().classes("items-center gap-1"):
                ui.icon(icon, color=color).classes("text-lg")
                ui.label(step).classes(f"text-sm {'font-semibold' if is_active else ''}")
            if i < len(steps) - 1:
                ui.icon("chevron_right", color="grey").classes("text-sm")
    return row
