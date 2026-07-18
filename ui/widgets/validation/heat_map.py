"""Validation heat map widget (Sprint 7)."""

from typing import Callable, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def _cell_color(status: str) -> str:
    return {"pass": "bg-green-100 text-green-700",
            "warn": "bg-yellow-100 text-yellow-700",
            "fail": "bg-red-100 text-red-700"}.get(status, "bg-gray-100 text-gray-500")


def render_heat_map(
    rows: List[str],
    columns: List[str],
    data: Dict[str, Dict[str, str]],
    on_cell_click: Callable,
) -> None:
    section_header("Validation Heat Map")
    with ui.card().classes("w-full p-4 overflow-x-auto"):
        with ui.table(
            rows=[{"store": r, **data.get(r, {})} for r in rows],
            row_key="store",
            columns=[
                {"name": "store", "label": "Store", "field": "store", "align": "left"},
                *[{"name": c, "label": c, "field": c, "align": "center"} for c in columns],
            ],
        ).classes("w-full"):
            pass
