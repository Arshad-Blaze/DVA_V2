"""Operation Layer — Main orchestrator.

Receives OperationContext and executes the supplied ExecutionPlan.
Only orchestrates — never makes business decisions.
"""

import time
from typing import Callable, Dict, List, Optional

from dav_platform.core.contracts import (
    CanonicalDataset,
    ExecutionMetadata,
    ExecutionResult,
    ExecutionState,
    ExecutionStepResult,
    OperationContext,
)
from dav_platform.operations.dispatcher import get_handler
from dav_platform.operations.executor import execute_step
from dav_platform.operations.state import StateManager
from dav_platform.operations.progress import ProgressTracker
from dav_platform.operations.retry import RetryPolicy
from dav_platform.operations.logging import ExecutionLogger


class OperationEngine:
    """Orchestrates execution of OperationContext plans.

    Receives an OperationContext from the Requirement Layer and executes
    the supplied ExecutionPlan step by step.

    This engine NEVER:
    - Makes business decisions
    - Determines workflows
    - Aggregates data
    - Calculates values
    - Validates business rules
    - Generates reports

    It only orchestrates.
    """

    def __init__(
        self,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        self._retry_policy = retry_policy or RetryPolicy()
        self._cancelled = False

    def execute(
        self,
        context: OperationContext,
        dataset: Optional[CanonicalDataset] = None,
        handlers: Optional[Dict[str, Callable]] = None,
    ) -> ExecutionResult:
        """Execute the operation plan.

        Args:
            context: OperationContext from Requirement Layer
            dataset: CanonicalDataset to process
            handlers: Dict of action -> handler for step dispatching

        Returns:
            ExecutionResult with step outcomes
        """
        from dav_platform.operations.dispatcher import register_handler

        # Register handlers
        if handlers:
            for action, handler_fn in handlers.items():
                register_handler(action, handler_fn)

        state = StateManager()
        tracker = ProgressTracker(len(context.execution_plan))
        logger = ExecutionLogger()
        step_results: List[ExecutionStepResult] = []

        overall_start = time.time()
        # Don't reset _cancelled here — allow pre-cancellation

        logger.execution_started(context.recommended_workflow)
        tracker.start()
        state.transition(ExecutionState.RUNNING)

        for step in context.execution_plan:
            if self._cancelled:
                state.transition(ExecutionState.CANCELLED)
                tracker.set_state(ExecutionState.CANCELLED)
                logger.warning(f"Execution cancelled at step {step.step_number}")
                break

            tracker.update_step(step.step_number, step.action)

            # Check if handler exists
            handler = get_handler(step.action)
            if handler is None:
                if step.required:
                    # Required step with no handler — fail
                    result = ExecutionStepResult(
                        step_number=step.step_number,
                        action=step.action,
                        state=ExecutionState.FAILED,
                        error=f"No handler for required action: {step.action}",
                    )
                    step_results.append(result)
                    tracker.complete_step(step.step_number, 0)
                    logger.step_failed(step.step_number, step.action, f"No handler: {step.action}", 0)

                    if not step.required:
                        continue
                    # Required step failed — abort
                    state.transition(ExecutionState.FAILED)
                    tracker.set_state(ExecutionState.FAILED)
                    break
                else:
                    # Optional step with no handler — skip
                    result = ExecutionStepResult(
                        step_number=step.step_number,
                        action=step.action,
                        state=ExecutionState.SKIPPED,
                    )
                    step_results.append(result)
                    tracker.complete_step(step.step_number, 0)
                    logger.step_skipped(step.step_number, step.action, "No handler registered")
                    continue

            # Execute step
            result = execute_step(
                step=step,
                handler=handler,
                dataset=dataset,
                context=context,
                retry_policy=self._retry_policy,
                logger=logger,
            )
            step_results.append(result)
            tracker.complete_step(step.step_number, result.elapsed_seconds)

            if result.state == ExecutionState.FAILED and step.required:
                state.transition(ExecutionState.FAILED)
                tracker.set_state(ExecutionState.FAILED)
                break

        overall_elapsed = time.time() - overall_start

        # Determine final outcome
        if self._cancelled:
            final_state = ExecutionState.CANCELLED
            outcome = "cancelled"
        elif any(r.state == ExecutionState.FAILED for r in step_results if
                 any(s.required for s in context.execution_plan if s.step_number == r.step_number)):
            final_state = ExecutionState.FAILED
            outcome = "failed"
        elif all(r.state in (ExecutionState.COMPLETED, ExecutionState.SKIPPED) for r in step_results):
            final_state = ExecutionState.COMPLETED
            outcome = "success"
        else:
            final_state = ExecutionState.COMPLETED
            outcome = "partial"

        state.transition(final_state) if final_state != state.state else None
        tracker.finish() if final_state == ExecutionState.COMPLETED else None

        logger.execution_completed(outcome, overall_elapsed)

        # Build metadata
        completed = sum(1 for r in step_results if r.state == ExecutionState.COMPLETED)
        failed = sum(1 for r in step_results if r.state == ExecutionState.FAILED)
        skipped = sum(1 for r in step_results if r.state == ExecutionState.SKIPPED)

        errors = [r.error for r in step_results if r.error]
        warnings = []
        if failed > 0:
            warnings.append(f"{failed} step(s) failed")
        if skipped > 0:
            warnings.append(f"{skipped} step(s) skipped")

        metadata = ExecutionMetadata(
            workflow=context.recommended_workflow,
            total_steps=len(context.execution_plan),
            completed_steps=completed,
            failed_steps=failed,
            skipped_steps=skipped,
            execution_duration=overall_elapsed,
            warnings=warnings,
            errors=errors,
            outcome=outcome,
        )

        return ExecutionResult(
            state=final_state,
            step_results=step_results,
            metadata=metadata,
            logs=logger.logs,
            warnings=warnings,
            errors=errors,
        )

    def cancel(self):
        """Request cancellation of the current execution."""
        self._cancelled = True
