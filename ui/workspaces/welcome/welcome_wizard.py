from typing import Callable, Optional
from nicegui import ui


class WelcomeWizard:
    def __init__(self, welcome_service, theme_service, project_service,
                 connection_service, demo_service, on_complete: Optional[Callable] = None,
                 on_dismiss: Optional[Callable] = None):
        self._welcome = welcome_service
        self._theme = theme_service
        self._project = project_service
        self._connection = connection_service
        self._demo = demo_service
        self._on_complete = on_complete
        self._on_dismiss = on_dismiss
        self._container: Optional[ui.column] = None

    def render(self, container) -> None:
        self._container = container
        with container:
            with ui.card().classes("w-full max-w-3xl mx-auto p-8"):
                self._render_header()
                self._render_step_content()
                self._render_navigation()

    def _render_header(self) -> None:
        step = self._welcome.current_step_info
        total = self._welcome.total_estimated_time
        with ui.column().classes("w-full"):
            ui.label("Welcome to DVA Platform v2").classes("text-2xl font-bold")
            ui.label(f"Estimated setup time: {total}").classes("text-sm text-gray-500")
            with ui.row().classes("w-full gap-1 my-4"):
                for i, s in enumerate(self._welcome.get_steps()):
                    is_active = i == self._welcome.current_step
                    is_done = i < self._welcome.current_step
                    color = "bg-green-500" if is_done else "bg-blue-500" if is_active else "bg-gray-300"
                    with ui.column().classes("items-center flex-1"):
                        with ui.icon(s["icon"]).classes(f"{color} text-white rounded-full p-2 text-sm"):
                            pass
                        ui.label(s["label"]).classes(f"text-xs {'font-bold' if is_active else ''} text-center")
            ui.separator()

    def _render_step_content(self) -> None:
        step_idx = self._welcome.current_step
        with ui.column().classes("w-full py-4 min-h-[200px]"):
            if step_idx == 0:
                self._render_welcome_step()
            elif step_idx == 1:
                self._render_theme_step()
            elif step_idx == 2:
                self._render_project_step()
            elif step_idx == 3:
                self._render_connection_step()
            elif step_idx == 4:
                self._render_detection_step()
            elif step_idx == 5:
                self._render_canonical_step()
            elif step_idx == 6:
                self._render_ready_step()

    def _render_welcome_step(self) -> None:
        ui.label("Get started with DVA").classes("text-xl font-semibold")
        ui.label("This wizard will help you set up your first project in about 8 minutes.").classes("text-gray-500 mt-2")
        with ui.column().classes("mt-4 gap-2"):
            ui.label("You will:").classes("font-medium")
            for s in self._welcome.get_steps()[1:-1]:
                ui.label(f"  {s['icon']}  {s['label']} (~{s['estimated']})").classes("text-sm")
        with ui.row().classes("mt-6 gap-4"):
            ui.button("Start Demo", on_click=self._start_demo, icon="play_arrow").props("color=primary")
            ui.button("Skip Demo", on_click=lambda: self._welcome.next_step()).props("flat")

    def _render_theme_step(self) -> None:
        ui.label("Choose Your Theme").classes("text-xl font-semibold")
        ui.label("Select a visual theme for the platform.").classes("text-gray-500 mt-2")
        with ui.row().classes("mt-4 gap-4"):
            themes = [
                ("light", "Light", "light_mode", "bg-white text-gray-900 border"),
                ("dark", "Dark", "dark_mode", "bg-gray-900 text-white border-gray-700"),
                ("system", "System", "brightness_auto", "bg-gray-100 text-gray-900"),
                ("high_contrast", "High Contrast", "contrast", "bg-black text-white border-white"),
            ]
            for theme_id, label, icon, style in themes:
                is_selected = self._welcome.get_preference("theme", "light") == theme_id
                with ui.card().classes(f"cursor-pointer p-4 text-center min-w-[120px] {style} {'ring-2 ring-blue-500' if is_selected else ''}").on("click", lambda t=theme_id: self._select_theme(t)):
                    ui.icon(icon).classes("text-2xl")
                    ui.label(label).classes("text-sm mt-1")
        ui.label("You can change this later in Settings.").classes("text-xs text-gray-400 mt-4")

    def _render_project_step(self) -> None:
        ui.label("Create Your First Project").classes("text-xl font-semibold")
        ui.label("A project organizes your data processing pipeline.").classes("text-gray-500 mt-2")
        with ui.column().classes("mt-4 gap-3"):
            name_input = ui.input("Project Name", placeholder="e.g., Retail Analysis Q1").classes("w-full")
            desc_input = ui.input("Description (optional)", placeholder="Brief description").classes("w-full")
            source_input = ui.input("Data Source (optional)", placeholder="Path to data directory").classes("w-full")
            def _create_project():
                name = name_input.value.strip() or "My Project"
                self._project.create_project(name, desc_input.value or "", source_input.value or "")
                self._welcome.set_preference("project_name", name)
                self._welcome.next_step()
            ui.button("Create Project", on_click=_create_project, icon="check").props("color=primary")

    def _render_connection_step(self) -> None:
        ui.label("Create a Data Connection").classes("text-xl font-semibold")
        ui.label("Connect to your data source to begin processing.").classes("text-gray-500 mt-2")
        with ui.column().classes("mt-4 gap-3"):
            type_select = ui.select(
                label="Connection Type",
                options=[{"label": "Local Filesystem", "value": "local"}, {"label": "SSH", "value": "ssh"}, {"label": "MFT", "value": "mft"}],
                value="local"
            ).classes("w-full")
            name_input = ui.input("Connection Name", placeholder="e.g., My Data Folder").classes("w-full")
            path_input = ui.input("Directory Path", placeholder="/path/to/data").classes("w-full")
            def _create_connection():
                name = name_input.value.strip() or "My Connection"
                ctype = type_select.value or "local"
                self._connection.add_connection(name, ctype, path_input.value or "/")
                self._welcome.set_preference("connection_name", name)
                self._welcome.next_step()
            ui.button("Create Connection", on_click=_create_connection, icon="check").props("color=primary")

    def _render_detection_step(self) -> None:
        ui.label("Run Detection").classes("text-xl font-semibold")
        ui.label("Detection analyzes your data file format automatically.").classes("text-gray-500 mt-2")
        ui.label("In this step, DVA will detect the file format, encoding, delimiter, and column layout.").classes("text-sm mt-2")
        ui.label("You can run detection from the Detection workspace after setup.").classes("text-sm text-gray-400 mt-4")
        def _next():
            self._welcome.next_step()
        ui.button("Continue", on_click=_next, icon="arrow_forward").props("color=primary").classes("mt-4")

    def _render_canonical_step(self) -> None:
        ui.label("Business Mapping").classes("text-xl font-semibold")
        ui.label("Map your data columns to DVA's business schema.").classes("text-gray-500 mt-2")
        ui.label("Business mapping transforms your raw data into a standardized format for analysis.").classes("text-sm mt-2")
        ui.label("You can configure mappings in the Canonical workspace.").classes("text-sm text-gray-400 mt-4")
        def _next():
            self._welcome.next_step()
        ui.button("Continue", on_click=_next, icon="arrow_forward").props("color=primary").classes("mt-4")

    def _render_ready_step(self) -> None:
        ui.icon("check_circle").classes("text-green-500 text-5xl")
        ui.label("You're All Set!").classes("text-xl font-semibold mt-2")
        ui.label("DVA is ready to use. You can now explore your project and start processing data.").classes("text-gray-500 mt-2")
        with ui.column().classes("mt-4 gap-1"):
            prefs = self._welcome._preferences
            if "theme" in prefs:
                ui.label(f"Theme: {prefs['theme']}").classes("text-sm")
            if "project_name" in prefs:
                ui.label(f"Project: {prefs['project_name']}").classes("text-sm")
            if "connection_name" in prefs:
                ui.label(f"Connection: {prefs['connection_name']}").classes("text-sm")
        def _finish():
            self._welcome.complete()
            if self._on_complete:
                self._on_complete()
        ui.button("Start Using DVA", on_click=_finish, icon="rocket_launch").props("color=primary").classes("mt-4")

    def _render_navigation(self) -> None:
        step_idx = self._welcome.current_step
        total = self._welcome.step_count
        with ui.row().classes("w-full justify-between items-center mt-6"):
            if step_idx > 0:
                ui.button("Back", on_click=lambda: self._welcome.prev_step(), icon="arrow_back").props("flat")
            else:
                ui.label("")
            ui.label(f"Step {step_idx + 1} of {total}").classes("text-sm text-gray-400")
            if step_idx == 0:
                ui.label("")
            elif step_idx < total - 1:
                ui.button("Skip", on_click=lambda: self._welcome.next_step(), icon="arrow_forward").props("flat")

    def _select_theme(self, theme_id: str) -> None:
        self._welcome.set_preference("theme", theme_id)
        self._theme.set_theme(theme_id)
        self._welcome._notify()

    def _start_demo(self) -> None:
        if self._demo:
            ok = self._demo.start_demo()
            if not ok:
                ui.notify("Failed to initialize demo mode. Please try again or skip demo.", type="negative")
                return
        self._welcome.set_preference("started_demo", True)
        self._welcome.complete()
        if self._on_complete:
            self._on_complete()
