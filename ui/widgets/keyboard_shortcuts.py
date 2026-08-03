from typing import Dict


DEFAULT_SHORTCUTS = {
    "Ctrl+H": "Navigate to Home",
    "Ctrl+P": "Navigate to Projects",
    "Ctrl+N": "New Project",
    "Ctrl+S": "Save current state",
    "Ctrl+B": "Toggle sidebar",
    "Ctrl+I": "Toggle inspector",
    "Ctrl+D": "Toggle dark mode",
    "Ctrl+E": "Navigate to Detection",
    "Ctrl+M": "Navigate to Canonical (Mapping)",
    "Ctrl+R": "Navigate to Reports",
    "Ctrl+A": "Navigate to Administration",
    "Ctrl+/": "Show keyboard shortcuts",
    "Escape": "Close dialog / Go back",
}


class KeyboardShortcutManager:
    def __init__(self):
        self._shortcuts: Dict[str, str] = dict(DEFAULT_SHORTCUTS)

    def get_all(self) -> Dict[str, str]:
        return dict(self._shortcuts)

    def get_display_list(self) -> list:
        return [{"keys": k, "action": v} for k, v in self._shortcuts.items()]
