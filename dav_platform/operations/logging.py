"""Structured execution logging."""

from datetime import datetime, timezone
from typing import List, Optional

from dav_platform.core.contracts import OperationLog


class ExecutionLogger:
    """Maintains structured execution logs."""

    def __init__(self):
        self._logs: List[OperationLog] = []

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def info(self, message: str, step: Optional[int] = None, action: str = "", **kwargs):
        """Log an info message."""
        self._logs.append(OperationLog(
            timestamp=self._now(),
            level="info",
            step_number=step,
            action=action,
            message=message,
            metadata=kwargs,
        ))

    def warning(self, message: str, step: Optional[int] = None, action: str = "", **kwargs):
        """Log a warning message."""
        self._logs.append(OperationLog(
            timestamp=self._now(),
            level="warning",
            step_number=step,
            action=action,
            message=message,
            metadata=kwargs,
        ))

    def error(self, message: str, step: Optional[int] = None, action: str = "", **kwargs):
        """Log an error message."""
        self._logs.append(OperationLog(
            timestamp=self._now(),
            level="error",
            step_number=step,
            action=action,
            message=message,
            metadata=kwargs,
        ))

    def step_started(self, step_number: int, action: str):
        """Log step start."""
        self.info(f"Step {step_number} started: {action}", step=step_number, action=action)

    def step_completed(self, step_number: int, action: str, duration: float):
        """Log step completion."""
        self.info(
            f"Step {step_number} completed: {action} ({duration:.3f}s)",
            step=step_number,
            action=action,
            duration_seconds=duration,
        )

    def step_failed(self, step_number: int, action: str, error: str, duration: float):
        """Log step failure."""
        self.error(
            f"Step {step_number} failed: {action} — {error} ({duration:.3f}s)",
            step=step_number,
            action=action,
            duration_seconds=duration,
        )

    def step_skipped(self, step_number: int, action: str, reason: str):
        """Log step skip."""
        self.warning(f"Step {step_number} skipped: {action} — {reason}", step=step_number, action=action)

    def retry_attempt(self, step_number: int, attempt: int, error: str):
        """Log retry attempt."""
        self.warning(
            f"Step {step_number} retry attempt {attempt}: {error}",
            step=step_number,
        )

    def execution_started(self, workflow: str):
        self.info(f"Execution started: workflow={workflow}")

    def execution_completed(self, outcome: str, duration: float):
        self.info(f"Execution completed: outcome={outcome} ({duration:.3f}s)")

    @property
    def logs(self) -> List[OperationLog]:
        return list(self._logs)

    def get_logs_for_step(self, step_number: int) -> List[OperationLog]:
        return [l for l in self._logs if l.step_number == step_number]
