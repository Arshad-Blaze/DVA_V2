"""Home workspace — Professional dashboard.

Sprint 2.5: Shows recent projects from persistence, resume session.
"""

from nicegui import ui
from ui.widgets.cards import info_card, metric_card, section_header
from ui.shared import project_svc, session_svc, conn_svc, notify_svc
from ui.widgets.guidance_bar import render_guidance


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
]


def render():
    render_guidance("home")
    with ui.card().classes("w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-xl"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column():
                ui.label("DVA Platform v2").classes("text-2xl font-bold")
                ui.label("Retail Data Processing Platform").classes("text-sm opacity-80")
            ui.label("v2.0.0").classes("text-xs opacity-60")

    if project_svc().current_project:
        cp = project_svc().current_project
        with ui.card().classes("w-full p-3 border-l-4 border-primary mt-2 card-hover"):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("history", color="primary").classes("text-xl")
                    ui.label(f"Resume Project: {cp['name']}").classes("text-sm font-semibold")
                ui.button("Continue", color="primary", size="sm",
                          on_click=lambda: None).props("dense").tooltip("Resume this project")

    ui.space().classes("h-4")
    section_header("Quick Start")
    with ui.row().classes("w-full gap-4"):
        for title, desc, icon, color in QUICK_ACTIONS:
            info_card(title, desc, icon, color)

    ui.space().classes("h-4")
    section_header("Platform Status")
    with ui.row().classes("w-full gap-4"):
        metric_card("Layers", "9", "layers", "primary")
        metric_card("Tests", "993", "science", "positive")
        metric_card("Status", "Ready", "check_circle", "positive")
        metric_card("Version", "2.0.0", "tag", "info")

    recent = project_svc().recent_projects(4)
    if recent:
        ui.space().classes("h-4")
        section_header("Recent Projects")
        with ui.grid(columns=2).classes("w-full gap-3"):
            for p in recent:
                with ui.card().classes("p-3 cursor-pointer card-hover").props("clickable"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("folder", color="primary").classes("text-xl")
                        with ui.column().classes("gap-0"):
                            ui.label(p["name"]).classes("text-sm font-semibold")
                            ui.label(p.get("description", "")).classes("text-xs text-gray-500")

    ui.space().classes("h-4")
    section_header("Architecture — All Layers Frozen")
    with ui.grid(columns=3).classes("w-full gap-3"):
        for name, desc, icon, frozen in BACKEND_LAYERS:
            with ui.card().classes("p-3 card-hover"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon(icon, color="positive" if frozen else "grey").classes("text-xl")
                    with ui.column().classes("gap-0"):
                        ui.label(name).classes("text-sm font-semibold")
                        ui.label(desc).classes("text-xs text-gray-500")
                if frozen:
                    ui.label("FROZEN").classes("text-xs text-positive mt-1")

    ui.space().classes("h-4")
    section_header("Projects")
    with ui.card().classes("w-full p-4"):
        projects = project_svc().list_projects()
        if projects:
            for p in projects[:5]:
                with ui.row().classes("items-center gap-3 py-1"):
                    ui.icon("folder", color="primary").classes("text-sm")
                    ui.label(p["name"]).classes("text-sm font-semibold min-w-20")
                    ui.label(p.get("description", "")).classes("text-sm text-gray-500")
        else:
            ui.label("No projects yet. Create one to get started.").classes("text-sm text-gray-400")
