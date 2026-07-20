from nicegui import ui


def render_empty_state(icon: str = "inbox", title: str = "No data available",
                      description: str = "", action_label: str = "",
                      action_callback=None) -> None:
    with ui.column().classes("w-full items-center justify-center py-16 gap-4"):
        ui.icon(icon).classes("text-6xl text-gray-300")
        ui.label(title).classes("text-xl font-semibold text-gray-500")
        if description:
            ui.label(description).classes("text-sm text-gray-400 text-center max-w-md")
        if action_label and action_callback:
            ui.button(action_label, on_click=action_callback).props("flat color=primary")
