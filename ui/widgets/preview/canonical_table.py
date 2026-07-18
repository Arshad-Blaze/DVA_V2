"""Business dataset preview table widget."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_canonical_table(
    columns: List[Dict[str, Any]],
    rows: List[Dict[str, Any]],
    row_count: int,
) -> None:
    section_header("Business Dataset Preview")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label(f"{row_count:,} rows · {len(columns)} columns").classes("text-sm text-gray-500")
            with ui.row().classes("gap-2"):
                ui.input(placeholder="Search...").classes("min-w-32").props("dense outlined")
                ui.select(
                    ["All", "Dairy", "Produce", "Bakery", "Meat", "Beverages"],
                    value="All",
                    label="Category",
                ).props("dense outlined").classes("min-w-28")

        with ui.table(
            rows=rows,
            row_key="upc",
            columns=columns,
            pagination={"rowsPerPage": 10},
        ).classes("w-full"):
            pass
