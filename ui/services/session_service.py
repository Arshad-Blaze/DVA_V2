"""Session service — UI session state manager.

Delegates to a shared WorkspaceContext when available for
persistence and cross-service state consistency.
When no context is provided, maintains independent state.
"""

from typing import Any, Dict, List, Optional

from ui.services.workspace_context import WorkspaceContext


class SessionService:
    """UI session state manager.

    When a WorkspaceContext is provided, reads/writes for
    workspace/theme/preferences are delegated to the shared context.
    """

    def __init__(self, context: Optional[WorkspaceContext] = None):
        self._context = context
        self._execution_status: str = "idle"
        self._workspace_params: Dict[str, Any] = {}

        # Fallback state when no context is provided
        self._fallback_current_workspace: str = "home"
        self._fallback_current_project: str = ""
        self._fallback_theme: str = "light"
        self._fallback_sidebar_collapsed: bool = False
        self._fallback_inspector_visible: bool = True
        self._fallback_nav_history: List[str] = []

    # ------------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------------

    @property
    def current_workspace(self) -> str:
        if self._context:
            return self._context.current_workspace
        return self._fallback_current_workspace

    @current_workspace.setter
    def current_workspace(self, value: str) -> None:
        if self._context:
            self._context.current_workspace = value
        else:
            if value != self._fallback_current_workspace:
                self._fallback_nav_history.append(self._fallback_current_workspace)
            self._fallback_current_workspace = value

    # ------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------

    @property
    def current_project(self) -> str:
        if self._context and self._context.current_project_id:
            return self._context.current_project_id
        return self._fallback_current_project

    @current_project.setter
    def current_project(self, value: str) -> None:
        if self._context:
            self._context.current_project_id = value if value else None
        self._fallback_current_project = value

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    @property
    def theme(self) -> str:
        if self._context:
            return self._context.theme
        return self._fallback_theme

    @theme.setter
    def theme(self, value: str) -> None:
        if self._context:
            self._context.theme = value
        self._fallback_theme = value

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------

    @property
    def sidebar_collapsed(self) -> bool:
        if self._context:
            return self._context.sidebar_collapsed
        return self._fallback_sidebar_collapsed

    @sidebar_collapsed.setter
    def sidebar_collapsed(self, value: bool) -> None:
        if self._context:
            self._context.sidebar_collapsed = value
        self._fallback_sidebar_collapsed = value

    # ------------------------------------------------------------------
    # Inspector
    # ------------------------------------------------------------------

    @property
    def inspector_visible(self) -> bool:
        if self._context:
            return self._context.inspector_visible
        return self._fallback_inspector_visible

    @inspector_visible.setter
    def inspector_visible(self, value: bool) -> None:
        if self._context:
            self._context.inspector_visible = value
        self._fallback_inspector_visible = value

    # ------------------------------------------------------------------
    # Execution status
    # ------------------------------------------------------------------

    @property
    def execution_status(self) -> str:
        return self._execution_status

    @execution_status.setter
    def execution_status(self, value: str) -> None:
        self._execution_status = value

    # ------------------------------------------------------------------
    # Navigation history
    # ------------------------------------------------------------------

    def nav_back(self) -> Optional[str]:
        if self._context:
            return self._context.nav_back()
        if self._fallback_nav_history:
            return self._fallback_nav_history.pop()
        return None

    # ------------------------------------------------------------------
    # Workspace params
    # ------------------------------------------------------------------

    def get_workspace_param(self, key: str, default: Any = None) -> Any:
        return self._workspace_params.get(key, default)

    def set_workspace_param(self, key: str, value: Any) -> None:
        self._workspace_params[key] = value

    def clear_workspace_params(self) -> None:
        self._workspace_params.clear()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        self._execution_status = "idle"
        self._workspace_params.clear()
        self._fallback_current_workspace = "home"
        self._fallback_current_project = ""
        self._fallback_theme = "light"
        self._fallback_sidebar_collapsed = False
        self._fallback_inspector_visible = True
        self._fallback_nav_history.clear()
        if self._context:
            self._context.reset()
