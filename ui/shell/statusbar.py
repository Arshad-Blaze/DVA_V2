"""Shell — Status bar."""

from datetime import datetime
from nicegui import ui
from ui.shared import perf_svc


def create_statusbar(session_svc) -> None:
    with ui.footer().classes("items-center justify-between px-4 py-1"):
        with ui.row().classes("items-center gap-4 text-xs text-gray-400"):
            ui.label(f"Layer: {session_svc.current_workspace.title()}")
            ui.label(f"State: {session_svc.execution_status.title()}")
            ui.label("Mem: -- MB")
            ui.label("Stream: idle")

        with ui.row().classes("items-center gap-4 text-xs text-gray-400"):
            ui.label("v2.0.0")
            startup = perf_svc().startup_time_ms
            ui.label(f"Startup: {startup:.0f}ms").classes("text-green-500" if startup < 1000 else "text-yellow-500")
            time_label = ui.label()
            ui.timer(1.0, lambda: time_label.set_text(datetime.now().strftime("%H:%M:%S")))
