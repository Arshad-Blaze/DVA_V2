from nicegui import ui


class LoadingIndicator:
    def __init__(self):
        self._container = None

    def show(self, container, message: str = "Loading...") -> None:
        with container:
            self._container = ui.row().classes("w-full justify-center items-center p-8 gap-4")
            with self._container:
                ui.spinner(size="lg")
                ui.label(message).classes("text-gray-500")

    def hide(self) -> None:
        if self._container:
            self._container.clear()
            self._container = None
