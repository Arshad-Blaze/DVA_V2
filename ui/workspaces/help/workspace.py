"""Help workspace — Documentation and support."""

from nicegui import ui
from ui.widgets.cards import section_header
from ui.shared import navigate_to
from ui.widgets.guidance_bar import render_guidance


def render():
    render_guidance("help")

    section_header("Getting Started")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center gap-3 py-2"):
            ui.icon("power", color="primary").classes("text-xl")
            with ui.column().classes("gap-0"):
                ui.label("1. Connect to a Data Source").classes("text-sm font-semibold")
                ui.label("Go to Connection workspace and connect to a local directory or remote server.").classes("text-xs text-gray-500")

        with ui.row().classes("items-center gap-3 py-2"):
            ui.icon("search", color="primary").classes("text-xl")
            with ui.column().classes("gap-0"):
                ui.label("2. Detect File Structure").classes("text-sm font-semibold")
                ui.label("Select a file in Detection to automatically detect format, delimiter, encoding, and columns.").classes("text-xs text-gray-500")

        with ui.row().classes("items-center gap-3 py-2"):
            ui.icon("transform", color="primary").classes("text-xl")
            with ui.column().classes("gap-0"):
                ui.label("3. Map Columns").classes("text-sm font-semibold")
                ui.label("In Canonical Mapping, map physical columns to business schema fields.").classes("text-xs text-gray-500")

        with ui.row().classes("items-center gap-3 py-2"):
            ui.icon("calculate", color="primary").classes("text-xl")
            with ui.column().classes("gap-0"):
                ui.label("4. Configure & Execute").classes("text-sm font-semibold")
                ui.label("Set requirements, configure operations, and run the processing pipeline.").classes("text-xs text-gray-500")

    section_header("Pipeline Overview")
    with ui.card().classes("w-full p-4"):
        stages = [
            ("home", "Home", "Dashboard"),
            ("projects", "Projects", "Create and manage projects"),
            ("connection", "Connection", "Connect to data sources"),
            ("detection", "Detection", "Detect file structure and format"),
            ("canonical", "Canonical", "Map columns to business schema"),
            ("preview", "Preview", "Review mapped data"),
            ("requirement", "Requirement", "Set analysis goals"),
            ("operation", "Operation", "Configure execution plan"),
            ("processing", "Processing", "Run processing pipeline"),
            ("validation", "Validation", "Validate results"),
            ("reports", "Reports", "Generate reports"),
            ("administration", "Administration", "System management"),
        ]
        with ui.grid(columns=3).classes("w-full gap-3"):
            for ws_id, name, desc in stages:
                with ui.card().classes("p-3 cursor-pointer").on("click", lambda w=ws_id: navigate_to(w)):
                    ui.label(name).classes("text-sm font-semibold text-primary")
                    ui.label(desc).classes("text-xs text-gray-500")

    section_header("Keyboard Shortcuts")
    with ui.card().classes("w-full p-4"):
        shortcuts = [
            ("Ctrl+S", "Save current workspace state"),
            ("Ctrl+K", "Quick navigation"),
            ("Ctrl+F", "Search"),
            ("Ctrl+E", "Export data"),
        ]
        for key, desc in shortcuts:
            with ui.row().classes("items-center gap-4 py-1"):
                ui.badge(key, color="primary").classes("text-xs font-mono min-w-20")
                ui.label(desc).classes("text-sm")
