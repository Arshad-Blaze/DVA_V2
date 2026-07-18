"""Progress tracking for execution."""

import time
from dataclasses import dataclass, field
from typing import List, Optional

from dav_platform.core.contracts import ExecutionStep, ExecutionState


@dataclass
class ProgressInfo:
    """Current execution progress."""
    current_step: int = 0
    total_steps: int = 0
    progress_percent: float = 0.0
    elapsed_seconds: float = 0.0
    estimated_remaining: float = 0.0
    current_action: str = ""
    state: ExecutionState = ExecutionState.PENDING
    warnings: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)


class ProgressTracker:
    """Tracks execution progress."""

    def __init__(self, total_steps: int = 0):
        self._total_steps = total_steps
        self._current_step = 0
        self._start_time: Optional[float] = None
        self._step_times: List[float] = []
        self._warnings: List[str] = []
        self._messages: List[str] = []
        self._state = ExecutionState.PENDING

    def start(self):
        """Start tracking."""
        self._start_time = time.time()
        self._state = ExecutionState.RUNNING

    def update_step(self, step_number: int, action: str):
        """Update current step."""
        self._current_step = step_number
        self._messages.append(f"Step {step_number}: {action}")

    def complete_step(self, step_number: int, elapsed: float):
        """Record step completion."""
        self._step_times.append(elapsed)

    def add_warning(self, warning: str):
        self._warnings.append(warning)

    def set_state(self, state: ExecutionState):
        self._state = state

    def finish(self):
        """Finish tracking."""
        self._state = ExecutionState.COMPLETED

    def get_progress(self) -> ProgressInfo:
        """Get current progress."""
        elapsed = 0.0
        if self._start_time:
            elapsed = time.time() - self._start_time

        percent = 0.0
        estimated_remaining = 0.0
        if self._total_steps > 0:
            percent = (self._current_step / self._total_steps) * 100
            if self._step_times and self._current_step > 0:
                avg_step = sum(self._step_times) / len(self._step_times)
                remaining_steps = self._total_steps - self._current_step
                estimated_remaining = avg_step * remaining_steps

        current_action = ""
        if self._messages:
            current_action = self._messages[-1]

        return ProgressInfo(
            current_step=self._current_step,
            total_steps=self._total_steps,
            progress_percent=min(percent, 100.0),
            elapsed_seconds=elapsed,
            estimated_remaining=estimated_remaining,
            current_action=current_action,
            state=self._state,
            warnings=list(self._warnings),
            messages=list(self._messages),
        )
