from typing import Any, Callable, Dict, Optional
from nicegui import ui


class LazyLoader:
    def __init__(self):
        self._rendered = False
        self._content = None

    def render(self, render_fn: Callable, container=None) -> None:
        if not self._rendered:
            self._content = render_fn()
            self._rendered = True

    def reset(self) -> None:
        self._rendered = False
        self._content = None

    @property
    def is_rendered(self) -> bool:
        return self._rendered
