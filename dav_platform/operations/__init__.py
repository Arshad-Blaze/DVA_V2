"""Operation Layer — Orchestration engine.

Executes the plan supplied by the Requirement Layer.
Only orchestrates — never makes business decisions.
"""

from dav_platform.operations.engine import OperationEngine
from dav_platform.operations.dispatcher import (
    register_handler,
    get_handler,
    clear_handlers,
    dispatch_step,
)
from dav_platform.operations.executor import execute_step
from dav_platform.operations.state import StateManager
from dav_platform.operations.progress import ProgressTracker, ProgressInfo
from dav_platform.operations.retry import RetryPolicy, RetryState
from dav_platform.operations.logging import ExecutionLogger
from dav_platform.operations.exceptions import (
    OperationError,
    StepExecutionError,
    CancellationError,
    RetryExhaustedError,
)

__all__ = [
    "OperationEngine",
    "register_handler",
    "get_handler",
    "clear_handlers",
    "dispatch_step",
    "execute_step",
    "StateManager",
    "ProgressTracker",
    "ProgressInfo",
    "RetryPolicy",
    "RetryState",
    "ExecutionLogger",
    "OperationError",
    "StepExecutionError",
    "CancellationError",
    "RetryExhaustedError",
]
