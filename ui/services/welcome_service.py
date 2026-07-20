from typing import Any, Dict, List, Optional, Callable


WIZARD_STEPS = [
    {"id": "welcome", "label": "Welcome", "icon": "home", "estimated": "30s"},
    {"id": "theme", "label": "Choose Theme", "icon": "palette", "estimated": "30s"},
    {"id": "project", "label": "Create Project", "icon": "folder", "estimated": "1m"},
    {"id": "connection", "label": "Create Connection", "icon": "power", "estimated": "2m"},
    {"id": "detection", "label": "Run Detection", "icon": "search", "estimated": "30s"},
    {"id": "canonical", "label": "Business Mapping", "icon": "transform", "estimated": "3m"},
    {"id": "ready", "label": "Ready", "icon": "check_circle", "estimated": ""},
]

TOTAL_ESTIMATED_TIME = "8 minutes"


class WelcomeService:
    def __init__(self):
        self._current_step: int = 0
        self._completed: bool = False
        self._dismissed: bool = False
        self._preferences: Dict[str, Any] = {}
        self._on_change: Optional[Callable] = None

    @property
    def current_step(self) -> int:
        return self._current_step

    @property
    def current_step_info(self) -> Dict[str, Any]:
        return dict(WIZARD_STEPS[self._current_step])

    def next_step(self) -> bool:
        if self._current_step < len(WIZARD_STEPS) - 1:
            self._current_step += 1
            self._notify()
            return True
        return False

    def prev_step(self) -> bool:
        if self._current_step > 0:
            self._current_step -= 1
            self._notify()
            return True
        return False

    def go_to_step(self, step_index: int) -> bool:
        if 0 <= step_index < len(WIZARD_STEPS):
            self._current_step = step_index
            self._notify()
            return True
        return False

    def set_preference(self, key: str, value: Any) -> None:
        self._preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self._preferences.get(key, default)

    @property
    def is_completed(self) -> bool:
        return self._completed

    def complete(self) -> None:
        self._completed = True
        self._notify()

    @property
    def is_dismissed(self) -> bool:
        return self._dismissed

    def dismiss(self) -> None:
        self._dismissed = True
        self._notify()

    @property
    def step_count(self) -> int:
        return len(WIZARD_STEPS)

    @property
    def progress(self) -> float:
        return (self._current_step + 1) / len(WIZARD_STEPS) * 100

    @property
    def total_estimated_time(self) -> str:
        return TOTAL_ESTIMATED_TIME

    def get_steps(self) -> List[Dict[str, Any]]:
        return [dict(s) for s in WIZARD_STEPS]

    def reset(self) -> None:
        self._current_step = 0
        self._completed = False
        self._dismissed = False
        self._preferences.clear()
        self._notify()

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
