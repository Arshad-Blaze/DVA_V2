"""Expected vs Actual comparison widget (Sprint 7)."""

from typing import Any, Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_comparison(data: List[Dict[str, Any]]) -> None:
    section_header("Expected vs Actual Comparison")
    with ui.card().classes("w-full p-4"):
        with ui.table(
            rows=data,
            row_key="metric",
            columns=[
                {"name": "metric", "label": "Metric", "field": "metric", "align": "left"},
                {"name": "expected", "label": "Expected", "field": "expected", "align": "right"},
                {"name": "actual", "label": "Actual", "field": "actual", "align": "right"},
                {"name": "diff", "label": "Difference", "field": "diff", "align": "right"},
                {"name": "pct", "label": "Δ %", "field": "pct", "align": "right"},
            ],
        ).classes("w-full"):
            pass
