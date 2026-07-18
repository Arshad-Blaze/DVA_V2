"""Home workspace — Professional dashboard."""

from datetime import datetime
from nicegui import ui
from ui.widgets.cards import info_card, metric_card, section_header, workspace_card


BACKEND_LAYERS = [
    ("Connection", "Data access", "check", True),
    ("Detection", "File format discovery", "search", True),
    ("Canonical", "Schema normalization", "transform", True),
    ("Requirement", "Workflow planning", "assignment", True),
    ("Operation", "Execution orchestration", "play_circle", True),
    ("Processing", "Computations", "calculate", True),
    ("Validation", "Business rules", "verified", True),
    ("Output", "Reports & export", "file_present", True),
    ("Flush", "Lifecycle & cleanup", "delete_sweep", True),
]

QUICK_ACTIONS = [
    ("New Project", "Create a new data project", "add_circle", "#4361ee"),
    ("Open Project", "Browse existing projects", "folder_open", "#4caf50"),
    ("Documentation", "View platform docs", "menu_book", "#ff9800"),
    ("Run Demo", "Run a demo pipeline", "play_arrow", "#9c27b0"),
]


def render():
    # Welcome banner
    with ui.card().classes("w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-xl"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column():
                ui.label("DVA Platform v2").classes("text-2xl font-bold")
                ui.label("Retail Data Processing Platform").classes("text-sm opacity-80")
            ui.label(f"v2.0.0").classes("text-xs opacity-60")

    # Quick actions
    ui.space().classes("h-4")
    section_header("Quick Start")
    with ui.row().classes("w-full gap-4"):
        for title, desc, icon, color in QUICK_ACTIONS:
            info_card(title, desc, icon, color)

    # Metrics
    ui.space().classes("h-4")
    section_header("Platform Status")
    with ui.row().classes("w-full gap-4"):
        metric_card("Layers", "9", "layers", "primary")
        metric_card("Tests", "931", "science", "positive")
        metric_card("Status", "Ready", "check_circle", "positive")
        metric_card("Version", "2.0.0", "tag", "info")

    # Architecture status
    ui.space().classes("h-4")
    section_header("Architecture — All Layers Frozen")
    with ui.grid(columns=3).classes("w-full gap-3"):
        for name, desc, icon, frozen in BACKEND_LAYERS:
            with ui.card().classes("p-3"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon(icon, color="positive" if frozen else "grey").classes("text-xl")
                    with ui.column().classes("gap-0"):
                        ui.label(name).classes("text-sm font-semibold")
                        ui.label(desc).classes("text-xs text-gray-500")
                if frozen:
                    ui.label("FROZEN").classes("text-xs text-positive mt-1")

    # Recent activity
    ui.space().classes("h-4")
    section_header("Recent Activity")
    with ui.card().classes("w-full p-4"):
        items = [
            ("Sprint 9", "Flush Layer completed", "done", "positive"),
            ("Sprint 8", "Output Layer completed", "done", "positive"),
            ("Sprint 7", "Validation Layer completed", "done", "positive"),
            ("Sprint 6", "Processing Layer completed", "done", "positive"),
        ]
        for sprint, desc, icon, color in items:
            with ui.row().classes("items-center gap-3 py-1"):
                ui.icon(icon, color=color).classes("text-sm")
                ui.label(sprint).classes("text-sm font-mono text-gray-500 min-w-20")
                ui.label(desc).classes("text-sm")
