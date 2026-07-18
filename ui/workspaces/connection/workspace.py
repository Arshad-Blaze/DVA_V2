"""Connection workspace — Data Source Configuration & File Browsing.

Sprint 2B: Connect to data sources, browse files, manage connections.
Sprint 2.5: Persistence auto-save via shared ConnectionService.
"""

from nicegui import ui
from ui.widgets.cards import section_header, info_card, empty_state, status_badge
from ui.services.connection_service import ConnectionType, CONNECTION_TYPES
from ui.shared import conn_svc, conn_ctrl


def add_connection_dialog() -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
        ui.label("Add Connection").classes("text-xl font-bold mb-4")
        name = ui.input("Connection Name", placeholder="My Data Source").classes("w-full")
        ctype = ui.select(
            {k: v["label"] for k, v in CONNECTION_TYPES.items()},
            label="Type", value=ConnectionType.LOCAL,
        ).classes("w-full mt-2")
        path = ui.input("Path", placeholder="/data/source").classes("w-full mt-2")
        desc = ui.input("Description", placeholder="Optional description").classes("w-full mt-2")
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Add", color="primary", on_click=lambda: (
                conn_ctrl().add_connection(name.value, ctype.value, path.value, desc.value),
                dialog.close(),
                refresh(),
            ))
    dialog.open()


def confirm_remove_dialog(cid: str, cname: str) -> None:
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
        ui.label("Remove Connection").classes("text-xl font-bold mb-4")
        ui.label(f'Remove "{cname}"? This does not delete source data.').classes("text-sm")
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Remove", color="negative", on_click=lambda: (
                conn_ctrl().remove_connection(cid),
                dialog.close(),
                refresh(),
            ))
    dialog.open()


def refresh() -> None:
    connections_container.clear()
    with connections_container:
        _render_connections()


def _render_browser() -> None:
    current = conn_svc().current_connection
    if not current:
        return

    conn = current
    ui.space().classes("h-4")
    section_header(f"File Browser — {conn['name']}")

    path = conn.get("path", "/")
    with ui.card().classes("w-full p-4"):
        ui.label(f"Path: {path}").classes("text-sm font-mono text-gray-500 mb-2")

        entries = conn_svc().browse_directory(path)
        if entries:
            for e in entries[:50]:
                icon = "folder" if e["is_dir"] else "description"
                size_str = f"{e['size']:,} B" if e["size"] > 0 else "-"
                with ui.row().classes("items-center gap-3 py-1 px-2 hover:bg-gray-50 rounded cursor-pointer"):
                    ui.icon(icon, color="primary" if e["is_dir"] else "grey").classes("text-lg")
                    ui.label(e["name"]).classes("text-sm font-mono")
                    ui.label(size_str).classes("text-xs text-gray-400")
                    ui.label(e["modified"].strftime("%Y-%m-%d %H:%M")).classes("text-xs text-gray-400")
        else:
            empty_state("No files found at this path", "folder_off")


def _render_connections():
    section_header("Data Source Connections")

    with ui.row().classes("w-full items-center justify-between mb-4"):
        ui.label(f"{len(conn_svc().list_connections())} connections").classes("text-sm text-gray-500")
        ui.button("+ Add Connection", color="primary", on_click=add_connection_dialog)

    connections = conn_svc().list_connections()
    if not connections:
        empty_state("No connections configured. Add a data source to get started.", "power_off")
        return

    current_cid = conn_svc().current_connection_id
    for c in connections:
        is_current = c["id"] == current_cid
        tinfo = conn_svc().get_type_info(c["conn_type"])
        is_connected = c["status"] == "connected"

        with ui.card().classes("w-full p-4 cursor-pointer").props("clickable") as card:
            with ui.row().classes("items-center justify-between w-full"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon(tinfo["icon"], color=tinfo["color"]).classes("text-2xl")
                    with ui.column().classes("gap-0"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(c["name"]).classes("text-lg font-semibold")
                            if is_current:
                                ui.label("ACTIVE").classes("text-xs bg-primary text-white px-2 py-0.5 rounded")
                        if c.get("description"):
                            ui.label(c["description"]).classes("text-sm text-gray-500")
                        if c.get("path"):
                            ui.label(c["path"]).classes("text-xs font-mono text-gray-400")
                        if is_connected and c.get("connected_at"):
                            ui.label(f'Connected: {c["connected_at"].strftime("%Y-%m-%d %H:%M")}').classes("text-xs text-gray-400")

                with ui.row().classes("items-center gap-2"):
                    if is_connected:
                        ui.button(icon="link_off", on_click=lambda cid=c["id"]: (
                            conn_ctrl().disconnect(cid),
                            refresh(),
                        )).props("flat round dense size=sm color=warning")
                    else:
                        ui.button(icon="link", on_click=lambda cid=c["id"]: (
                            conn_ctrl().connect(cid),
                            refresh(),
                        )).props("flat round dense size=sm color=positive")
                    ui.button(icon="delete", on_click=lambda cid=c["id"], cn=c["name"]: (
                        confirm_remove_dialog(cid, cn),
                    )).props("flat round dense size=sm color=negative")

    _render_browser()


connections_container = ui.column()


def render():
    _render_connections()
