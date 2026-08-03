"""Performance charts widget (Sprint 6B)."""

from typing import Dict, List
from nicegui import ui
from ui.widgets.cards import section_header


def render_performance_charts(data: Dict[str, List[float]]) -> None:
    section_header("Performance")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=2).classes("w-full gap-6"):
            with ui.column().classes("w-full"):
                ui.label("Memory Trend").classes("text-sm font-semibold mb-2")
                memory = data.get("memory_trend", [0] * 10)
                if max(memory) > 0:
                    ui.linear_progress(value=memory[-1] / max(memory), size="8px", color="blue").classes("w-full")
                    with ui.row().classes("w-full justify-between text-xs text-gray-400"):
                        ui.label("0 MB")
                        ui.label(f"{memory[-1]:.0f} MB")
                else:
                    ui.label("Waiting for data...").classes("text-xs text-gray-400 italic")

            with ui.column().classes("w-full"):
                ui.label("CPU Trend").classes("text-sm font-semibold mb-2")
                cpu = data.get("cpu_trend", [0] * 10)
                if max(cpu) > 0:
                    ui.linear_progress(value=cpu[-1] / 100, size="8px", color="green").classes("w-full")
                    with ui.row().classes("w-full justify-between text-xs text-gray-400"):
                        ui.label("0%")
                        ui.label(f"{cpu[-1]:.0f}%")
                else:
                    ui.label("Waiting for data...").classes("text-xs text-gray-400 italic")

        if memory and len(memory) > 1:
            ui.separator().classes("my-3")
            memory_str = " → ".join(f"{m:.0f}" for m in memory[-5:])
            cpu_str = " → ".join(f"{c:.0f}%" for c in cpu[-5:])
            with ui.grid(columns=2).classes("w-full gap-4"):
                ui.label(f"Memory: {memory_str} MB").classes("text-xs text-gray-500")
                ui.label(f"CPU: {cpu_str}").classes("text-xs text-gray-500")
