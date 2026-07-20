from typing import Any, Callable, Dict, List, Optional
from nicegui import ui


class VirtualTable:
    def __init__(self, columns: List[Dict[str, Any]], rows: List[Dict[str, Any]],
                 page_size: int = 50, container: Optional = None):
        self._columns = columns
        self._rows = rows
        self._page_size = page_size
        self._current_page = 0
        self._total_pages = max(1, (len(rows) + page_size - 1) // page_size)
        self._container = container
        self._table_elements: List = []

    def render(self, container) -> None:
        with container:
            with ui.column().classes("w-full"):
                if not self._rows:
                    with ui.row().classes("w-full justify-center p-8"):
                        ui.label("No data available").classes("text-gray-400")
                    return

                with ui.row().classes("w-full justify-between items-center mb-2"):
                    with ui.row().classes("items-center gap-2"):
                        ui.button(icon="first_page", on_click=lambda: self._go_to_page(0)).props("flat dense")
                        ui.button(icon="chevron_left", on_click=self._prev_page).props("flat dense")
                        ui.label(f"Page {self._current_page + 1} of {self._total_pages}").classes("text-sm")
                        ui.button(icon="chevron_right", on_click=self._next_page).props("flat dense")
                        ui.button(icon="last_page", on_click=lambda: self._go_to_page(self._total_pages - 1)).props("flat dense")
                    ui.label(f"{len(self._rows)} total rows").classes("text-xs text-gray-400")

                with ui.table(columns=self._columns, rows=self._get_page_rows(), row_key="id").classes("w-full") as table:
                    pass

                self._table_elements = [table]

    def _get_page_rows(self) -> List[Dict[str, Any]]:
        start = self._current_page * self._page_size
        end = start + self._page_size
        return self._rows[start:end]

    def _prev_page(self) -> None:
        if self._current_page > 0:
            self._current_page -= 1
            self._refresh()

    def _next_page(self) -> None:
        if self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._refresh()

    def _go_to_page(self, page: int) -> None:
        if 0 <= page < self._total_pages:
            self._current_page = page
            self._refresh()

    def _refresh(self) -> None:
        if self._table_elements:
            table = self._table_elements[0]
            table.rows = self._get_page_rows()
            table.update()
