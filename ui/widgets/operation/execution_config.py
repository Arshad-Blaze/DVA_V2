"""Execution configuration widget (Sprint 6A)."""

from typing import Any, Callable, Dict
from nicegui import ui
from ui.widgets.cards import section_header


def render_execution_config(config: Dict[str, Any], on_update: Callable) -> None:
    section_header("Execution Configuration")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=2).classes("w-full gap-6"):
            with ui.column().classes("gap-3"):
                ui.label("Basic Settings").classes("text-sm font-semibold")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("cloud", color="blue").classes("text-lg")
                    ui.label("Streaming").classes("text-sm")
                    streaming = ui.switch(value=config.get("streaming", True))
                    streaming.on("update:model-value", lambda e: on_update("streaming", e.args))

                with ui.row().classes("items-center gap-2"):
                    ui.icon("grid_view", color="blue").classes("text-lg")
                    ui.label("Chunk Size").classes("text-sm")
                    ui.select([5000, 10000, 25000, 50000], value=config.get("chunk_size", 10000),
                              on_change=lambda e: on_update("chunk_size", e.value)).props("dense outlined").classes("min-w-28")

                with ui.row().classes("items-center gap-2"):
                    ui.icon("group_work", color="blue").classes("text-lg")
                    ui.label("Parallel Workers").classes("text-sm")
                    ui.select([1, 2, 4, 8], value=config.get("parallel_workers", 2),
                              on_change=lambda e: on_update("parallel_workers", e.value)).props("dense outlined").classes("min-w-20")

            with ui.column().classes("gap-3"):
                ui.label("Advanced Options").classes("text-sm font-semibold")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("folder", color="orange").classes("text-lg")
                    ui.label("Output Location").classes("text-sm")
                    ui.input(value=config.get("output_location", "./output"),
                             on_change=lambda e: on_update("output_location", e.value)).props("dense outlined").classes("min-w-32")

                with ui.row().classes("items-center gap-2"):
                    ui.icon("science", color="orange").classes("text-lg")
                    ui.label("Dry Run").classes("text-sm")
                    ui.switch(value=config.get("dry_run", False),
                              on_change=lambda e: on_update("dry_run", e.args))

                with ui.row().classes("items-center gap-2"):
                    ui.icon("play_circle", color="orange").classes("text-lg")
                    ui.label("Execution Mode").classes("text-sm")
                    ui.label(config.get("mode", "Aggregate + Calculate")).classes("text-xs font-semibold")
