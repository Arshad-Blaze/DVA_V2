"""Shell — Status bar."""

from datetime import datetime
from nicegui import ui


def create_statusbar(session_svc) -> None:
    with ui.footer().classes("items-center justify-between px-4 py-1"):
        with ui.row().classes("items-center gap-4 text-xs text-gray-400"):
            ui.label(f"Layer: {session_svc.current_workspace.title()}")
            ui.label(f"State: {session_svc.execution_status.title()}")
            ui.label("Mem: -- MB")
            ui.label("Stream: idle")

        with ui.row().classes("items-center gap-4 text-xs text-gray-400"):
            ui.label("v2.0.0")
            time_label = ui.label()
            ui.timer(1.0, lambda: time_label.set_text(datetime.now().strftime("%H:%M:%S")))
