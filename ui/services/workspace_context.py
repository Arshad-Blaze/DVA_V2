"""WorkspaceContext — single shared UI state object.

Becomes the single source of truth for all UI session state.
Services read from and write to this context rather than
maintaining independent state.
"""

from typing import Any, Dict, List, Optional, Callable


class WorkspaceContext:
    """Central UI state shared across all services and controllers.

    Never couples to backend. Never touches the filesystem.
    """

    def __init__(self):
        # Navigation
        self._current_workspace: str = "home"
        self._navigation_history: List[str] = []

        # Project
        self._current_project_id: Optional[str] = None
        self._recent_projects: List[str] = []

        # Connection
        self._current_connection_id: Optional[str] = None
        self._recent_connections: List[str] = []

        # Preferences
        self._theme: str = "light"
        self._sidebar_collapsed: bool = False
        self._inspector_visible: bool = True

        # Detection / Canonical / Execution (seeded for future use)
        self._current_detection_session: Optional[str] = None
        self._current_canonical_session: Optional[str] = None
        self._current_execution_id: Optional[str] = None

        # Callbacks
        self._on_change: Optional[Callable] = None

    # ------------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------------

    @property
    def current_workspace(self) -> str:
        return self._current_workspace

    @current_workspace.setter
    def current_workspace(self, value: str) -> None:
        if value != self._current_workspace:
            self._navigation_history.append(self._current_workspace)
        self._current_workspace = value
        self._notify()

    @property
    def navigation_history(self) -> List[str]:
        return list(self._navigation_history)

    @navigation_history.setter
    def navigation_history(self, value: List[str]) -> None:
        self._navigation_history = list(value)

    def nav_back(self) -> Optional[str]:
        if self._navigation_history:
            return self._navigation_history.pop()
        return None

    # ------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------

    @property
    def current_project_id(self) -> Optional[str]:
        return self._current_project_id

    @current_project_id.setter
    def current_project_id(self, value: Optional[str]) -> None:
        self._current_project_id = value
        self._notify()

    @property
    def recent_projects(self) -> List[str]:
        return list(self._recent_projects)

    @recent_projects.setter
    def recent_projects(self, value: List[str]) -> None:
        self._recent_projects = list(value)

    def add_recent_project(self, project_id: str) -> None:
        if project_id in self._recent_projects:
            self._recent_projects.remove(project_id)
        self._recent_projects.insert(0, project_id)
        self._recent_projects = self._recent_projects[:10]
        self._notify()

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    @property
    def current_connection_id(self) -> Optional[str]:
        return self._current_connection_id

    @current_connection_id.setter
    def current_connection_id(self, value: Optional[str]) -> None:
        self._current_connection_id = value
        self._notify()

    @property
    def recent_connections(self) -> List[str]:
        return list(self._recent_connections)

    @recent_connections.setter
    def recent_connections(self, value: List[str]) -> None:
        self._recent_connections = list(value)

    def add_recent_connection(self, connection_id: str) -> None:
        if connection_id in self._recent_connections:
            self._recent_connections.remove(connection_id)
        self._recent_connections.insert(0, connection_id)
        self._recent_connections = self._recent_connections[:10]
        self._notify()

    # ------------------------------------------------------------------
    # Preferences / Theme
    # ------------------------------------------------------------------

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str) -> None:
        self._theme = value
        self._notify()

    @property
    def sidebar_collapsed(self) -> bool:
        return self._sidebar_collapsed

    @sidebar_collapsed.setter
    def sidebar_collapsed(self, value: bool) -> None:
        self._sidebar_collapsed = value
        self._notify()

    @property
    def inspector_visible(self) -> bool:
        return self._inspector_visible

    @inspector_visible.setter
    def inspector_visible(self, value: bool) -> None:
        self._inspector_visible = value
        self._notify()

    # ------------------------------------------------------------------
    # Session state export / restore
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_workspace": self._current_workspace,
            "navigation_history": self._navigation_history,
            "current_project_id": self._current_project_id,
            "current_connection_id": self._current_connection_id,
            "recent_projects": self._recent_projects,
            "recent_connections": self._recent_connections,
            "theme": self._theme,
            "sidebar_collapsed": self._sidebar_collapsed,
            "inspector_visible": self._inspector_visible,
            "version": 1,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self._current_workspace = data.get("current_workspace", "home")
        self._navigation_history = data.get("navigation_history", [])
        self._current_project_id = data.get("current_project_id")
        self._current_connection_id = data.get("current_connection_id")
        self._recent_projects = data.get("recent_projects", [])
        self._recent_connections = data.get("recent_connections", [])
        self._theme = data.get("theme", "light")
        self._sidebar_collapsed = data.get("sidebar_collapsed", False)
        self._inspector_visible = data.get("inspector_visible", True)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        self._current_workspace = "home"
        self._navigation_history.clear()
        self._current_project_id = None
        self._current_connection_id = None
        self._recent_projects.clear()
        self._recent_connections.clear()
        self._theme = "light"
        self._sidebar_collapsed = False
        self._inspector_visible = True
        self._notify()

    # ------------------------------------------------------------------
    # Change notification
    # ------------------------------------------------------------------

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
