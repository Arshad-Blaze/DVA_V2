from nicegui import ui


class LoadingOverlay:
    def __init__(self):
        self._dialog = None

    def show(self, message: str = "Loading...") -> None:
        self._dialog = ui.dialog().classes("bg-transparent")
        with self._dialog, ui.card().classes("p-8 items-center gap-4"):
            ui.spinner(size="xl")
            ui.label(message).classes("text-gray-500")
        self._dialog.open()

    def hide(self) -> None:
        if self._dialog:
            self._dialog.close()
            self._dialog = None
