"""Step executor — executes individual steps with retry support."""

import time
from typing import Any, Callable, Dict, Optional

from dav_platform.core.contracts import (
    ExecutionStep,
    ExecutionState,
    ExecutionStepResult,
)
from dav_platform.operations.retry import RetryPolicy, RetryState
from dav_platform.operations.logging import ExecutionLogger


def execute_step(
    step: ExecutionStep,
    handler: Callable,
    dataset: Any = None,
    context: Any = None,
    options: Optional[Dict] = None,
    retry_policy: Optional[RetryPolicy] = None,
    logger: Optional[ExecutionLogger] = None,
) -> ExecutionStepResult:
    """Execute a single step with retry support.

    Args:
        step: The step to execute
        handler: Callable that performs the step
        dataset: The canonical dataset
        context: The operation context
        options: Additional options
        retry_policy: Retry policy for failed steps
        logger: Execution logger

    Returns:
        ExecutionStepResult with outcome
    """
    if retry_policy is None:
        retry_policy = RetryPolicy()

    retry_state = RetryState()
    options = options or {}

    while True:
        start = time.time()
        try:
            if logger:
                logger.step_started(step.step_number, step.action)

            result = handler(step=step, dataset=dataset, context=context, options=options)
            elapsed = time.time() - start

            if logger:
                logger.step_completed(step.step_number, step.action, elapsed)

            return ExecutionStepResult(
                step_number=step.step_number,
                action=step.action,
                state=ExecutionState.COMPLETED,
                result=result,
                elapsed_seconds=elapsed,
                retries=retry_state.attempt,
            )

        except Exception as e:
            elapsed = time.time() - start
            error_msg = str(e)

            if retry_policy.should_retry(retry_state.attempt, e):
                delay = retry_policy.get_delay(retry_state.attempt)
                retry_state.record_attempt(False, error_msg, delay)

                if logger:
                    logger.retry_attempt(step.step_number, retry_state.attempt, error_msg)

                time.sleep(delay)
                continue

            # No more retries — do NOT increment attempt again
            if logger:
                logger.step_failed(step.step_number, step.action, error_msg, elapsed)

            return ExecutionStepResult(
                step_number=step.step_number,
                action=step.action,
                state=ExecutionState.FAILED,
                error=error_msg,
                elapsed_seconds=elapsed,
                retries=retry_state.attempt,
                metadata={"exception_type": type(e).__name__},
            )
