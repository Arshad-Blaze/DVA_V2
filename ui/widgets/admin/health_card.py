"""System health card widget (Sprint 9)."""

from typing import Any, Dict
from nicegui import ui
from ui.widgets.cards import section_header, metric_card


STATUS_COLORS = {"healthy": "green", "warning": "orange", "critical": "red"}


def render_health_card(health: Dict[str, Any]) -> None:
    section_header("System Health")
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            cpu = health.get("cpu", {})
            metric_card("CPU", f"{cpu.get('usage_pct', 0):.0f}% ({cpu.get('cores', 0)} cores)",
                        "memory", STATUS_COLORS.get(cpu.get("status", "healthy"), "green"))
            mem = health.get("memory", {})
            metric_card("Memory", f"{mem.get('usage_pct', 0):.0f}% ({mem.get('used_gb', 0):.1f}/{mem.get('total_gb', 0)} GB)",
                        "storage", STATUS_COLORS.get(mem.get("status", "healthy"), "green"))
            streaming = health.get("streaming", {})
            metric_card("Streaming", "Active" if streaming.get("active") else "Inactive",
                        "stream", STATUS_COLORS.get(streaming.get("status", "healthy"), "green"))
            proj = health.get("projects", {})
            metric_card("Projects", f"{proj.get('active', 0)}/{proj.get('total', 0)} active",
                        "folder", STATUS_COLORS.get(proj.get("status", "healthy"), "green"))
            rpt = health.get("reports", {})
            metric_card("Reports", str(rpt.get("total", 0)),
                        "assessment", STATUS_COLORS.get(rpt.get("status", "healthy"), "green"))
            st = health.get("storage", {})
            pct = (st.get("used_mb", 0) / max(st.get("total_mb", 1), 1)) * 100
            metric_card("Storage", f"{pct:.0f}% ({st.get('used_mb', 0):.0f}/{st.get('total_mb', 0)} MB)",
                        "database", STATUS_COLORS.get(st.get("status", "healthy"), "green"))
            cache = health.get("cache", {})
            metric_card("Cache", f"{cache.get('entries', 0)} entries ({cache.get('size_mb', 0)} MB)",
                        "cached", STATUS_COLORS.get(cache.get("status", "healthy"), "green"))
            conn = health.get("connections", {})
            metric_card("Connections", f"{conn.get('active', 0)}/{conn.get('total', 0)} active",
                        "link", STATUS_COLORS.get(conn.get("status", "healthy"), "green"))
        ver = health.get("version", {})
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label(f"App: {ver.get('app', '—')} | Backend: {ver.get('backend', '—')} | UI: {ver.get('ui', '—')}").classes("text-xs text-gray-500")
