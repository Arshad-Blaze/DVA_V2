from typing import Any, Dict, List, Optional


class SessionService:
    """UI session state manager — tracks current project, workspace, preferences.

    NEVER couples to backend state.
    """

    def __init__(self):
        self._current_workspace: str = "home"
        self._current_project: str = ""
        self._execution_status: str = "idle"
        self._user_preferences: Dict[str, Any] = {
            "theme": "light",
            "sidebar_collapsed": False,
            "inspector_visible": True,
        }
        self._nav_history: List[str] = []
        self._workspace_params: Dict[str, Any] = {}

    @property
    def current_workspace(self) -> str:
        return self._current_workspace

    @current_workspace.setter
    def current_workspace(self, value: str) -> None:
        if value != self._current_workspace:
            self._nav_history.append(self._current_workspace)
        self._current_workspace = value

    @property
    def current_project(self) -> str:
        return self._current_project

    @current_project.setter
    def current_project(self, value: str) -> None:
        self._current_project = value

    @property
    def execution_status(self) -> str:
        return self._execution_status

    @execution_status.setter
    def execution_status(self, value: str) -> None:
        self._execution_status = value

    @property
    def theme(self) -> str:
        return self._user_preferences.get("theme", "light")

    @theme.setter
    def theme(self, value: str) -> None:
        self._user_preferences["theme"] = value

    @property
    def sidebar_collapsed(self) -> bool:
        return self._user_preferences.get("sidebar_collapsed", False)

    @sidebar_collapsed.setter
    def sidebar_collapsed(self, value: bool) -> None:
        self._user_preferences["sidebar_collapsed"] = value

    @property
    def inspector_visible(self) -> bool:
        return self._user_preferences.get("inspector_visible", True)

    @inspector_visible.setter
    def inspector_visible(self, value: bool) -> None:
        self._user_preferences["inspector_visible"] = value

    def nav_back(self) -> Optional[str]:
        if self._nav_history:
            return self._nav_history.pop()
        return None

    def get_workspace_param(self, key: str, default: Any = None) -> Any:
        return self._workspace_params.get(key, default)

    def set_workspace_param(self, key: str, value: Any) -> None:
        self._workspace_params[key] = value

    def clear_workspace_params(self) -> None:
        self._workspace_params.clear()

    def reset(self) -> None:
        self._current_workspace = "home"
        self._current_project = ""
        self._execution_status = "idle"
        self._nav_history.clear()
        self._workspace_params.clear()
