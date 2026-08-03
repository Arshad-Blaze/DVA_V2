"""Progress panel widget (Sprint 6B)."""

from nicegui import ui
from ui.widgets.cards import section_header, metric_card


def render_progress_panel(
    progress: float,
    stage_label: str,
    rows: int,
    elapsed: float,
    rows_per_sec: float,
) -> None:
    section_header("Progress")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between w-full mb-3"):
            ui.label(f"Current Stage: {stage_label}").classes("text-sm font-semibold")
            ui.label(f"{progress:.1f}%").classes("text-lg font-bold text-primary")

        ui.linear_progress(value=progress / 100, size="12px", color="primary").classes("w-full")

        with ui.grid(columns=4).classes("w-full gap-4 mt-3"):
            metric_card("Progress", f"{progress:.1f}%", "percent", "primary")
            metric_card("Rows Processed", f"{rows:,}", "table_rows", "blue")
            metric_card("Elapsed", f"{elapsed:.1f}s", "timer", "orange")
            metric_card("Rows/sec", f"{rows_per_sec:.1f}", "speed", "green")
