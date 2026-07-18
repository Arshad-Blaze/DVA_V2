"""Operation Layer exceptions."""

from typing import Optional


class OperationError(Exception):
    """Base exception for Operation Layer errors."""

    def __init__(self, message: str, step: Optional[int] = None, retryable: bool = False):
        super().__init__(message)
        self.step = step
        self.retryable = retryable


class StepExecutionError(OperationError):
    """Error during step execution."""
    pass


class CancellationError(OperationError):
    """Execution was cancelled."""
    pass


class RetryExhaustedError(OperationError):
    """All retry attempts exhausted."""
    pass
