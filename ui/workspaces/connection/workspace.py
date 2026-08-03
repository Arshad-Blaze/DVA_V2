"""Connection workspace — Data Source Configuration & File Browsing.

Dynamic forms based on connection type (LOCAL, SSH, MFT).
Supports Create, Edit, Delete, Duplicate, Test, Browse.
"""

from nicegui import ui
from ui.widgets.cards import section_header, empty_state
from ui.services.connection_service import ConnectionType, CONNECTION_TYPES
from ui.shared import conn_svc, conn_ctrl
from ui.widgets.guidance_bar import render_guidance


def manage_connection_dialog(existing_connection=None):
    is_edit = existing_connection is not None
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 max-w-xl dialog-panel"):
        with ui.row().classes("items-center gap-2 w-full mb-4"):
            ui.icon("settings_ethernet", color="primary").classes("text-2xl")
            ui.label(f"{'Edit' if is_edit else 'Add'} Connection").classes("text-xl font-bold")

        name_input = ui.input("Connection Name",
            value=existing_connection.get("name", "") if is_edit else "").classes("w-full input-field")

        if is_edit:
            conn_type = existing_connection["conn_type"]
            ui.label(f"Type: {CONNECTION_TYPES[conn_type]['label']}").classes("text-sm text-gray-500 mb-2")
        else:
            type_select = ui.select(
                {k: v["label"] for k, v in CONNECTION_TYPES.items()},
                label="Type", value=ConnectionType.LOCAL,
            ).classes("w-full")

        form_container = ui.column().classes("w-full gap-2 mt-2")
        field_widgets = {}

        def build_form(ctype):
            form_container.clear()
            field_widgets.clear()
            with form_container:
                form_config = conn_svc().get_form_config(ctype)
                for fd in form_config["fields"]:
                    key = fd["key"]
                    label = fd["label"]
                    ftype = fd["type"]
                    default = fd.get("default", "")
                    existing_val = existing_connection.get(key, default) if is_edit else default

                    if ftype == "password":
                        w = ui.input(label, value=existing_val, password=True).classes("w-full input-field")
                    elif ftype == "number":
                        w = ui.number(label, value=existing_val).classes("w-full input-field")
                    elif ftype == "select":
                        w = ui.select({o: o for o in fd["options"]}, label=label, value=existing_val).classes("w-full")
                    elif ftype == "directory":
                        with ui.row().classes("w-full items-center gap-2"):
                            w = ui.input(label, value=existing_val).classes("flex-1 input-field")
                            ui.button(icon="folder_open",
                                on_click=lambda inp=w: browse_directory_dialog(inp)).props("flat").tooltip("Browse directory")
                    elif ftype == "file":
                        w = ui.input(label, value=existing_val).classes("w-full input-field")
                    else:
                        w = ui.input(label, value=existing_val).classes("w-full input-field")
                    field_widgets[key] = w

                actions = form_config.get("actions", [])
                if actions:
                    with ui.row().classes("w-full gap-2 mt-2"):
                        if "test" in actions:
                            ui.button("Test Connection", icon="online_prediction",
                                on_click=lambda c=ctype: _test_connection(c)).props("outline").tooltip("Test this connection configuration")

        def _test_connection(ctype):
            vals = {k: w.value for k, w in field_widgets.items()}
            conn_ctrl().test_connection(ctype, **vals)

        def _save():
            name = name_input.value.strip()
            if not name:
                conn_ctrl()._notify_svc.warning("Connection name is required")
                return
            vals = {k: w.value for k, w in field_widgets.items()}
            if is_edit:
                vals["name"] = name
                conn_ctrl().update_connection(existing_connection["id"], **vals)
            else:
                ctype = type_select.value
                conn_ctrl().add_connection(name, ctype, **vals)
            dialog.close()
            refresh()

        build_form(existing_connection["conn_type"] if is_edit else ConnectionType.LOCAL)

        if not is_edit:
            def on_type_change(e):
                build_form(e.value)
            type_select.on_value_change(on_type_change)

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", color="primary", on_click=_save)

    dialog.open()


def browse_directory_dialog(target_input):
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 dialog-panel"):
        with ui.row().classes("items-center gap-2 w-full mb-4"):
            ui.icon("folder_open", color="primary").classes("text-2xl")
            ui.label("Browse Directory").classes("text-xl font-bold")
        path_display = ui.label(target_input.value or "/").classes("text-sm font-mono text-gray-500 mb-2")
        entries_container = ui.column().classes("w-full")

        def navigate(dir_path):
            path_display.set_text(dir_path)
            entries_container.clear()
            with entries_container:
                entries = conn_svc().browse_directory(dir_path)
                if not entries:
                    empty_state("Empty directory", "folder_off")
                for e in entries:
                    if e["is_dir"]:
                        with ui.row().classes("items-center gap-2 py-1 px-2 hover:bg-gray-50 rounded cursor-pointer"):
                            ui.icon("folder", color="primary").classes("text-lg")
                            ui.label(e["name"]).classes("text-sm font-mono flex-1")
                            ui.button(icon="arrow_forward",
                                on_click=lambda p=e["path"]: navigate(p)).props("flat round dense").tooltip("Open directory")

        navigate(target_input.value or "/")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Select", color="primary", on_click=lambda: (
                target_input.set_value(path_display.text),
                dialog.close(),
            ))
    dialog.open()


def confirm_remove_dialog(cid, cname):
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 dialog-panel"):
        with ui.row().classes("items-center gap-2 w-full mb-4"):
            ui.icon("link_off", color="negative").classes("text-2xl")
            ui.label("Remove Connection").classes("text-xl font-bold")
        ui.label(f'Remove "{cname}"? This does not delete source data.').classes("text-sm")
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Remove", color="negative", on_click=lambda: (
                conn_ctrl().remove_connection(cid),
                dialog.close(),
                refresh(),
            ))
    dialog.open()


def refresh():
    connections_container.clear()
    with connections_container:
        _render_connections()


def _render_browser():
    current = conn_svc().current_connection
    if not current:
        return

    conn = current
    conn_type = conn.get("conn_type", ConnectionType.LOCAL)
    if conn_type == ConnectionType.LOCAL:
        path = conn.get("directory", "/")
    else:
        path = conn.get("remote_directory", "/")

    ui.space().classes("h-4")
    section_header(f"File Browser — {conn['name']}")

    with ui.card().classes("w-full p-4"):
        ui.label(f"Path: {path}").classes("text-sm font-mono text-gray-500 mb-2")

        if conn_type == ConnectionType.LOCAL:
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
        else:
            entries = conn_svc().browse_directory(path)
            if not entries:
                empty_state(f"Remote directory browser not available for {CONNECTION_TYPES[conn_type]['label']}", "cloud_off")


def _render_connections():
    section_header("Data Source Connections")

    with ui.row().classes("w-full items-center justify-between mb-4"):
        ui.label(f"{len(conn_svc().list_connections())} connections").classes("text-sm text-gray-500")
        ui.button("+ Add Connection", color="primary", on_click=lambda: manage_connection_dialog())

    connections = conn_svc().list_connections()
    if not connections:
        empty_state("No connections configured. Add a data source to get started.", "power_off")
        return

    current_cid = conn_svc().current_connection_id
    for c in connections:
        is_current = c["id"] == current_cid
        tinfo = conn_svc().get_type_info(c["conn_type"])
        is_connected = c["status"] == "connected"

        with ui.card().classes("w-full p-4 cursor-pointer").props("clickable"):
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
                        if c.get("directory"):
                            ui.label(c["directory"]).classes("text-xs font-mono text-gray-400")
                        elif c.get("remote_directory"):
                            ui.label(c["remote_directory"]).classes("text-xs font-mono text-gray-400")
                        elif c.get("host"):
                            ui.label(f'{c.get("host")}:{c.get("port", "")}').classes("text-xs font-mono text-gray-400")
                        if is_connected and c.get("connected_at"):
                            ui.label(f'Connected: {c["connected_at"].strftime("%Y-%m-%d %H:%M")}').classes("text-xs text-gray-400")

                with ui.row().classes("items-center gap-2"):
                    if is_connected:
                        ui.button(icon="link_off", on_click=lambda cid=c["id"]: (
                            conn_ctrl().disconnect(cid),
                            refresh(),
                        )).props("flat round dense size=sm color=warning").tooltip("Disconnect")
                    else:
                        ui.button(icon="link", on_click=lambda cid=c["id"]: (
                            conn_ctrl().connect(cid),
                            refresh(),
                        )).props("flat round dense size=sm color=positive").tooltip("Connect")
                    ui.button(icon="edit", on_click=lambda c=c: (
                        manage_connection_dialog(c),
                    )).props("flat round dense size=sm").tooltip("Edit connection")
                    ui.button(icon="content_copy", on_click=lambda cid=c["id"]: (
                        conn_ctrl().duplicate_connection(cid),
                        refresh(),
                    )).props("flat round dense size=sm").tooltip("Duplicate connection")
                    ui.button(icon="delete", on_click=lambda cid=c["id"], cn=c["name"]: (
                        confirm_remove_dialog(cid, cn),
                    )).props("flat round dense size=sm color=negative").tooltip("Remove connection")

    _render_browser()


connections_container = ui.column()


def render():
    render_guidance("connection")
    _render_connections()
