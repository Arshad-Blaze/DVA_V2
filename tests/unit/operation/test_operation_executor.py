"""Tests for step executor."""

import time

import pytest

from dav_platform.core.contracts import ExecutionState, ExecutionStep
from dav_platform.operations.executor import execute_step
from dav_platform.operations.retry import RetryPolicy
from dav_platform.operations.logging import ExecutionLogger


class TestExecuteStep:
    def test_successful_execution(self):
        def handler(step, dataset=None, context=None, options=None):
            return "result"

        step = ExecutionStep(step_number=1, action="load", description="Load")
        result = execute_step(step, handler)
        assert result.state == ExecutionState.COMPLETED
        assert result.result == "result"
        assert result.elapsed_seconds >= 0

    def test_failed_execution(self):
        def handler(step, dataset=None, context=None, options=None):
            raise ValueError("test error")

        step = ExecutionStep(step_number=1, action="load", description="Load")
        result = execute_step(step, handler)
        assert result.state == ExecutionState.FAILED
        assert "test error" in result.error

    def test_retry_on_failure(self):
        call_count = [0]

        def handler(step, dataset=None, context=None, options=None):
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("transient error")
            return "recovered"

        step = ExecutionStep(step_number=1, action="load", description="Load")
        policy = RetryPolicy(max_retries=3, delay_seconds=0.01)
        result = execute_step(step, handler, retry_policy=policy)
        assert result.state == ExecutionState.COMPLETED
        assert result.retries == 2
        assert result.result == "recovered"

    def test_retry_exhausted(self):
        def handler(step, dataset=None, context=None, options=None):
            raise ValueError("permanent error")

        step = ExecutionStep(step_number=1, action="load", description="Load")
        policy = RetryPolicy(max_retries=2, delay_seconds=0.01)
        result = execute_step(step, handler, retry_policy=policy)
        assert result.state == ExecutionState.FAILED
        assert result.retries == 2

    def test_no_retry_on_non_retryable(self):
        def handler(step, dataset=None, context=None, options=None):
            raise TypeError("not retryable")

        step = ExecutionStep(step_number=1, action="load", description="Load")
        policy = RetryPolicy(max_retries=3, retry_on=(ValueError,))
        result = execute_step(step, handler, retry_policy=policy)
        assert result.state == ExecutionState.FAILED
        assert result.retries == 0

    def test_with_logger(self):
        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        logger = ExecutionLogger()
        step = ExecutionStep(step_number=1, action="load", description="Load")
        result = execute_step(step, handler, logger=logger)
        assert result.state == ExecutionState.COMPLETED
        assert len(logger.logs) >= 2  # started + completed
