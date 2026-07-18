"""Metadata explorer widget."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header
from dav_platform.core.contracts import CanonicalMetadata


def render_metadata_explorer(meta: CanonicalMetadata) -> None:
    section_header("Metadata Explorer")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=3).classes("w-full gap-4"):
            _meta_item("Transformation Strategy", meta.flatten_strategy.replace("_", " ").title())
            _meta_item("Quantity Strategy", meta.quantity_type.replace("_", " ").title())
            _meta_item("UOM Strategy", meta.uom_strategy.title())
            _meta_item("Ignored Columns", str(len(meta.ignored_columns)))
            _meta_item("Source Type", meta.source_file_type or "CSV")
            _meta_item("Encoding", meta.encoding.upper())
            _meta_item("Schema Version", "v2.0")
            _meta_item("Canonical Version", "v1.0")
            _meta_item("Warnings", str(len(meta.warnings)))

        if meta.transformation_log:
            ui.separator().classes("my-3")
            ui.label("Transformation Log").classes("text-sm font-semibold mb-2")
            for entry in meta.transformation_log:
                ui.label(f"• {entry}").classes("text-xs text-gray-500 ml-2")


def _meta_item(label: str, value: str) -> None:
    with ui.column().classes("gap-0"):
        ui.label(value).classes("text-sm font-semibold")
        ui.label(label).classes("text-xs text-gray-500")
