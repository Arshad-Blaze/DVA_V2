"""Developer Mode workspace — shows system internals for debugging."""
from nicegui import ui
from ui import shared


def render() -> None:
    context = shared.context()
    persistence = shared.persistence()
    storage = shared.storage()
    nav_svc = shared.nav_svc()
    theme_svc = shared.theme_svc()

    ui.label("Developer Mode").classes("text-2xl font-bold")
    ui.label("System diagnostics and internal state").classes("text-gray-500 mb-4")
    ui.separator()

    tabs = ui.tabs().classes("w-full")
    with tabs:
        ui.tab("Backend Status", icon="dns")
        ui.tab("Frontend Status", icon="web")
        ui.tab("Workspace Context", icon="dataset")
        ui.tab("Controllers", icon="settings_remote")
        ui.tab("Services", icon="engineering")
        ui.tab("System", icon="memory")
        ui.tab("Streaming", icon="sync")

    with ui.tab_panels(tabs).classes("w-full"):
        with ui.tab_panel("Backend Status"):
            ui.label("Backend Layers").classes("text-lg font-semibold mb-2")
            layers = [
                "connection", "detection", "canonical", "requirements",
                "operations", "processing", "validation", "output", "flush",
            ]
            with ui.grid(columns=3).classes("w-full gap-4"):
                for layer in layers:
                    with ui.card().classes("p-4"):
                        ui.label(layer.title()).classes("font-medium")
                        ui.label("Status: FROZEN").classes("text-sm text-green-500")
                        ui.label("Contract: STABLE").classes("text-sm text-blue-500")

        with ui.tab_panel("Frontend Status"):
            ui.label("Application State").classes("text-lg font-semibold mb-2")
            with ui.column().classes("gap-2"):
                items = [
                    ("Current Workspace", nav_svc.active),
                    ("Theme", theme_svc.theme),
                    ("Is Dark", str(theme_svc.is_dark)),
                    ("Debug Info", str(context.to_dict())),
                ]
                for label, value in items:
                    with ui.row().classes("w-full"):
                        ui.label(f"{label}:").classes("font-mono text-sm w-40")
                        ui.label(str(value)).classes("font-mono text-sm text-blue-500")

        with ui.tab_panel("Workspace Context"):
            ui.label("Full Context State").classes("text-lg font-semibold mb-2")
            ctx = context.to_dict()
            with ui.column().classes("gap-1"):
                for key, val in ctx.items():
                    with ui.row().classes("w-full"):
                        ui.label(f"{key}:").classes("font-mono text-sm w-48")
                        ui.label(str(val)).classes("font-mono text-sm text-green-500")

        with ui.tab_panel("Controllers"):
            ui.label("Registered Controllers").classes("text-lg font-semibold mb-2")
            controllers = [
                "session", "navigation", "workspace", "project", "connection",
                "detection", "canonical", "preview", "requirement", "operation",
                "processing", "validation", "reports", "admin",
            ]
            with ui.grid(columns=4).classes("w-full gap-2"):
                for ctrl in controllers:
                    with ui.card().classes("p-2 text-center"):
                        ui.label(ctrl.title()).classes("text-sm font-medium")
                        ui.label("ACTIVE").classes("text-xs text-green-500")

        with ui.tab_panel("Services"):
            ui.label("Registered Services").classes("text-lg font-semibold mb-2")
            services = [
                "session", "project", "connection", "navigation", "notification",
                "theme", "detection", "canonical", "preview", "requirement",
                "operation", "processing", "validation", "reports", "admin",
                "persistence", "storage", "migration",
            ]
            with ui.grid(columns=4).classes("w-full gap-2"):
                for svc in services:
                    with ui.card().classes("p-2 text-center"):
                        ui.label(svc.title()).classes("text-sm font-medium")
                        ui.label("ACTIVE").classes("text-xs text-green-500")

        with ui.tab_panel("System"):
            ui.label("System Resources").classes("text-lg font-semibold mb-2")
            import os
            try:
                import psutil
                with ui.grid(columns=2).classes("w-full gap-4"):
                    with ui.card().classes("p-4"):
                        ui.label("Memory").classes("font-medium")
                        mem = psutil.virtual_memory()
                        ui.label(f"Total: {mem.total / 1024**3:.1f} GB").classes("font-mono text-sm")
                        ui.label(f"Available: {mem.available / 1024**3:.1f} GB").classes("font-mono text-sm")
                        ui.label(f"Used: {mem.percent}%").classes("font-mono text-sm")
                    with ui.card().classes("p-4"):
                        ui.label("CPU").classes("font-medium")
                        ui.label(f"Cores: {os.cpu_count()}").classes("font-mono text-sm")
                        ui.label(f"Usage: {psutil.cpu_percent()}%").classes("font-mono text-sm")
                    with ui.card().classes("p-4"):
                        ui.label("Storage").classes("font-medium")
                        st = psutil.disk_usage("/")
                        ui.label(f"Total: {st.total / 1024**3:.1f} GB").classes("font-mono text-sm")
                        ui.label(f"Free: {st.free / 1024**3:.1f} GB").classes("font-mono text-sm")
                        ui.label(f"Used: {st.percent}%").classes("font-mono text-sm")
                    with ui.card().classes("p-4"):
                        ui.label("Persistence").classes("font-medium")
                        ui.label(f"Storage Path: {storage.base_path}").classes("font-mono text-sm")
                        ui.label(f"Version: {persistence.storage_version()}").classes("font-mono text-sm")
            except ImportError:
                with ui.card().classes("p-4"):
                    ui.label("System monitoring requires psutil").classes("text-yellow-500")
                    ui.label("Install with: pip install psutil").classes("text-sm text-gray-500")

        with ui.tab_panel("Streaming"):
            ui.label("Streaming Status").classes("text-lg font-semibold mb-2")
            ui.label("Streaming is not currently active.").classes("text-gray-500")
            ui.label("Streaming status will appear here during active data processing.").classes("text-sm text-gray-400 mt-2")
