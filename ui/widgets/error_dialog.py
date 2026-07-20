from typing import Optional, Callable
from nicegui import ui


def show_error_dialog(title: str = "Error", message: str = "An unexpected error occurred.",
                     detail: str = "", on_retry: Optional[Callable] = None,
                     on_close: Optional[Callable] = None) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
        with ui.column().classes("w-full gap-4"):
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon("error").classes("text-red-500 text-2xl")
                ui.label(title).classes("text-lg font-semibold")
            ui.separator()
            ui.label(message).classes("text-sm text-gray-600")
            if detail:
                ui.label(detail).classes("text-xs text-gray-400 font-mono bg-gray-100 p-2 rounded")
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                if on_retry:
                    ui.button("Retry", on_click=lambda: (dialog.close(), on_retry())).props("color=warning")
                ui.button("Close", on_click=lambda: (dialog.close(), on_close() if on_close else None)).props("flat")
    dialog.open()


def show_success_dialog(title: str = "Success", message: str = "Operation completed successfully.",
                       on_close: Optional[Callable] = None) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
        with ui.column().classes("w-full gap-4"):
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon("check_circle").classes("text-green-500 text-2xl")
                ui.label(title).classes("text-lg font-semibold")
            ui.separator()
            ui.label(message).classes("text-sm text-gray-600")
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("OK", on_click=lambda: (dialog.close(), on_close() if on_close else None)).props("color=primary")
    dialog.open()
