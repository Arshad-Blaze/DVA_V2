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
        with ui.table(rows=projects, row_key="name").classes("w-full text-sm"):
            with ui.thead():
                with ui.tr():
                    for col in ["name", "created", "modified", "retailer", "version", "status"]:
                        ui.th().text(col.title())
            with ui.tbody():
                for p in projects:
                    is_sel = selected and selected["name"] == p["name"]
                    with ui.tr().props("clickable" + (" bg-blue-50" if is_sel else "")):
                        with ui.td().on("click", lambda n=p["name"]: on_select(n)):
                            ui.label(p["name"]).classes("text-sm font-medium")
                        ui.td().text(p.get("created", "")).props("")
                        ui.td().text(p.get("modified", "")).props("")
                        ui.td().text(p.get("retailer", "")).props("")
                        ui.td().text(p.get("version", "")).props("")
                        with ui.td():
                            status = p.get("status", "")
                            color = "green" if status == "active" else "gray"
                            ui.badge(status, color=color)


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
        with ui.table(rows=executions, row_key="execution_id").classes("w-full text-sm"):
            with ui.thead():
                with ui.tr():
                    for col in ["execution_id", "project", "runtime", "status", "rows", "validation_score", "reports"]:
                        label = col.replace("_", " ").title()
                        ui.th().text(label)
            with ui.tbody():
                for e in executions:
                    is_sel = selected and selected["execution_id"] == e["execution_id"]
                    with ui.tr().props("clickable" + (" bg-blue-50" if is_sel else "")):
                        with ui.td().on("click", lambda xid=e["execution_id"]: on_select(xid)):
                            ui.label(e["execution_id"]).classes("text-sm font-medium")
                        ui.td().text(e.get("project", ""))
                        ui.td().text(e.get("runtime", ""))
                        with ui.td():
                            status = e.get("status", "")
                            color = "green" if status == "completed" else "red"
                            ui.badge(status, color=color)
                        ui.td().text(str(e.get("rows", 0)))
                        vs = e.get("validation_score", 0)
                        ui.td().text(f"{vs:.0f}%" if vs else "—")
                        ui.td().text(str(e.get("reports", 0)))
