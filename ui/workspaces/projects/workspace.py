"""Projects workspace — Project Management.

Sprint 2A: Create, open, rename, delete projects.
Sprint 2.5: Persistence auto-save via shared ProjectService.
"""

from nicegui import ui
from ui.widgets.cards import info_card, section_header, empty_state
from ui.shared import project_svc, project_ctrl
from ui.widgets.guidance_bar import render_guidance


def create_project_dialog() -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 dialog-panel"):
        with ui.column().classes("w-full gap-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("add_circle", color="primary").classes("text-2xl")
                ui.label("Create Project").classes("text-xl font-bold")
            name = ui.input("Project Name", placeholder="My Project").classes("w-full input-field")
            desc = ui.input("Description", placeholder="Brief description").classes("w-full input-field")
            source = ui.input("Source Path", placeholder="/data/source").classes("w-full input-field")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Create", color="primary", on_click=lambda: (
                    project_ctrl().create_project(name.value, desc.value, source.value),
                    dialog.close(),
                    refresh(),
                ))
    dialog.open()


def delete_project_dialog(pid: str, pname: str) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 dialog-panel"):
        with ui.column().classes("w-full gap-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("delete", color="negative").classes("text-2xl")
                ui.label("Delete Project").classes("text-xl font-bold")
            ui.label(f'Are you sure you want to delete "{pname}"?').classes("text-sm")
            ui.label("This action cannot be undone.").classes("text-xs text-gray-500")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Delete", color="negative", on_click=lambda: (
                    project_ctrl().delete_project(pid),
                    dialog.close(),
                    refresh(),
                ))
    dialog.open()


def rename_project_dialog(pid: str) -> None:
    p = project_svc().get_project(pid)
    if not p:
        return
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 dialog-panel"):
        with ui.column().classes("w-full gap-4"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("edit", color="primary").classes("text-2xl")
                ui.label("Rename Project").classes("text-xl font-bold")
            name = ui.input("Project Name", value=p["name"]).classes("w-full input-field")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Rename", color="primary", on_click=lambda: (
                    project_ctrl().rename_project(pid, name.value),
                    dialog.close(),
                    refresh(),
                ))
    dialog.open()


def refresh() -> None:
    projects_container.clear()
    with projects_container:
        _render_content()


def _render_projects_list():
    projects = project_svc().list_projects()
    if not projects:
        empty_state("No projects yet. Create one to get started.", "folder_open")
        return

    current_pid = project_svc().current_project_id
    for p in projects:
        is_current = p["id"] == current_pid
        with ui.card().classes("w-full p-4 cursor-pointer card-hover").props("clickable"):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("folder", color="primary").classes("text-2xl")
                    with ui.column().classes("gap-0"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(p["name"]).classes("text-lg font-semibold")
                            if is_current:
                                ui.label("OPEN").classes("text-xs bg-primary text-white px-2 py-0.5 rounded")
                            if p.get("source"):
                                ui.label(p["source"]).classes("text-xs text-gray-400")
                        ui.label(p.get("description", "")).classes("text-sm text-gray-500")
                        ui.label(f'Modified: {p["modified"].strftime("%Y-%m-%d %H:%M")}').classes("text-xs text-gray-400 mt-1")

                with ui.row().classes("items-center gap-1"):
                    if not is_current:
                        ui.button(icon="folder_open", on_click=lambda pid=p["id"]: (
                            project_ctrl().open_project(pid),
                            refresh(),
                        )).props("flat round dense size=sm").tooltip("Open project")
                    ui.button(icon="edit", on_click=lambda pid=p["id"]: (
                        rename_project_dialog(pid),
                    )).props("flat round dense size=sm").tooltip("Rename project")
                    ui.button(icon="delete", on_click=lambda pid=p["id"], pn=p["name"]: (
                        delete_project_dialog(pid, pn),
                    )).props("flat round dense size=sm color=negative").tooltip("Delete project")


projects_container = ui.column()


def _render_content():
    section_header("Project Management")

    with ui.row().classes("w-full gap-4 mb-6"):
        info_card("Create Project", "Create a new data project from scratch", "add_circle", "primary")
        info_card("Open Recent", "Open a recently used project", "history", "info")
        info_card("Browse All", "Browse all available projects", "folder_open", "positive")

    with ui.row().classes("w-full items-center justify-between"):
        ui.label("All Projects").classes("text-lg font-semibold")
        ui.button("+ New Project", color="primary", on_click=create_project_dialog).tooltip("Create a new project")

    ui.separator().classes("my-4")

    _render_projects_list()

    cp = project_svc().current_project
    if cp:
        ui.space().classes("h-4")
        section_header("Current Project")
        with ui.card().classes("w-full p-4"):
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label(cp["name"]).classes("text-xl font-bold")
                    ui.label(cp.get("description", "")).classes("text-sm text-gray-500")
                    if cp.get("source"):
                        ui.label(f"Source: {cp['source']}").classes("text-xs text-gray-400")
                ui.button("Close Project", color="warning", on_click=lambda: (
                    project_ctrl().close_project(),
                    refresh(),
                )).tooltip("Close the current project")


def render():
    render_guidance("projects")
    _render_content()
