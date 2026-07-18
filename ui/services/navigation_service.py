from typing import Dict, List, Optional, Callable


class NavigationService:
    """Manages navigation state: active item, history, disabled items."""

    def __init__(self):
        self._items: List[Dict] = []
        self._active: str = "home"
        self._disabled: set = set()
        self._on_change: Optional[Callable] = None

    def register(self, item: Dict) -> None:
        self._items.append(item)

    def register_many(self, items: List[Dict]) -> None:
        self._items.extend(items)

    @property
    def items(self) -> List[Dict]:
        return list(self._items)

    @property
    def active(self) -> str:
        return self._active

    def navigate(self, workspace_id: str) -> None:
        if workspace_id in self._disabled:
            return
        self._active = workspace_id
        if self._on_change:
            self._on_change(workspace_id)

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def disable(self, workspace_id: str) -> None:
        self._disabled.add(workspace_id)

    def enable(self, workspace_id: str) -> None:
        self._disabled.discard(workspace_id)

    def is_disabled(self, workspace_id: str) -> bool:
        return workspace_id in self._disabled

    def reset(self) -> None:
        self._active = "home"
        self._disabled.clear()
