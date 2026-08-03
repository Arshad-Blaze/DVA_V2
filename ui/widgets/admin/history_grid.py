"""Project & execution history grid widget (Sprint 9)."""

from typing import Any, Callable, Dict, List, Optional
from nicegui import ui
from ui.widgets.cards import section_header


def render_project_history(
    projects: List[Dict[str, Any]],
    selected: Optional[Dict[str, Any]],
    on_select: Callable,
) -> None:
    section_header("Project History")
    with ui.card().classes("w-full p-4"):
        if not projects:
            ui.label("No project history available.").classes("text-sm text-gray-500")
            return
        columns = [
            {"name": "name", "label": "Name", "field": "name", "sortable": True},
            {"name": "created", "label": "Created", "field": "created"},
            {"name": "modified", "label": "Modified", "field": "modified"},
            {"name": "retailer", "label": "Retailer", "field": "retailer"},
            {"name": "version", "label": "Version", "field": "version"},
            {"name": "status", "label": "Status", "field": "status"},
        ]
        rows = [
            {
                "name": p.get("name", ""),
                "created": p.get("created", ""),
                "modified": p.get("modified", ""),
                "retailer": p.get("retailer", ""),
                "version": p.get("version", ""),
                "status": p.get("status", ""),
            }
            for p in projects
        ]
        selected_name = selected.get("name") if selected else None
        with ui.table(rows=rows, columns=columns, row_key="name", selection="single",
                      on_select=lambda e: on_select(e.selection[0]["name"]) if e.selection else None).classes("w-full text-sm") as table:
            table.add_slot(
                "body-cell-status",
                '<td :props="props">'
                '<q-badge :color="props.value === \'active\' ? \'green\' : \'grey\'" :label="props.value" />'
                "</td>",
            )
            if selected_name is not None:
                table.selected = [r for r in rows if r["name"] == selected_name]


def render_execution_history(
    executions: List[Dict[str, Any]],
    selected: Optional[Dict[str, Any]],
    on_select: Callable,
) -> None:
    section_header("Execution History")
    with ui.card().classes("w-full p-4"):
        if not executions:
            ui.label("No execution history available.").classes("text-sm text-gray-500")
            return
        columns = [
            {"name": "execution_id", "label": "Execution ID", "field": "execution_id", "sortable": True},
            {"name": "project", "label": "Project", "field": "project"},
            {"name": "runtime", "label": "Runtime", "field": "runtime"},
            {"name": "status", "label": "Status", "field": "status"},
            {"name": "rows", "label": "Rows", "field": "rows"},
            {"name": "validation_score", "label": "Validation Score", "field": "validation_score"},
            {"name": "reports", "label": "Reports", "field": "reports"},
        ]
        rows = [
            {
                "execution_id": e.get("execution_id", ""),
                "project": e.get("project", ""),
                "runtime": e.get("runtime", ""),
                "status": e.get("status", ""),
                "rows": str(e.get("rows", 0)),
                "validation_score": f"{e['validation_score']:.0f}%" if e.get("validation_score") else "—",
                "reports": str(e.get("reports", 0)),
            }
            for e in executions
        ]
        selected_id = selected.get("execution_id") if selected else None
        with ui.table(rows=rows, columns=columns, row_key="execution_id", selection="single",
                      on_select=lambda e: on_select(e.selection[0]["execution_id"]) if e.selection else None).classes("w-full text-sm") as table:
            table.add_slot(
                "body-cell-status",
                '<td :props="props">'
                '<q-badge :color="props.value === \'completed\' ? \'green\' : \'red\'" :label="props.value" />'
                "</td>",
            )
            if selected_id is not None:
                table.selected = [r for r in rows if r["execution_id"] == selected_id]
