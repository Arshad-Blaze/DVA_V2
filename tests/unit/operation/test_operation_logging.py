"""Tests for execution logging."""

import pytest

from dav_platform.operations.logging import ExecutionLogger


class TestExecutionLogger:
    def test_info_log(self):
        logger = ExecutionLogger()
        logger.info("test message")
        assert len(logger.logs) == 1
        assert logger.logs[0].level == "info"
        assert logger.logs[0].message == "test message"

    def test_warning_log(self):
        logger = ExecutionLogger()
        logger.warning("test warning")
        assert logger.logs[0].level == "warning"

    def test_error_log(self):
        logger = ExecutionLogger()
        logger.error("test error")
        assert logger.logs[0].level == "error"

    def test_step_started(self):
        logger = ExecutionLogger()
        logger.step_started(1, "aggregate")
        assert len(logger.logs) == 1
        assert logger.logs[0].step_number == 1
        assert "aggregate" in logger.logs[0].message

    def test_step_completed(self):
        logger = ExecutionLogger()
        logger.step_completed(1, "aggregate", 0.5)
        assert "0.500s" in logger.logs[0].message

    def test_step_failed(self):
        logger = ExecutionLogger()
        logger.step_failed(1, "aggregate", "timeout", 1.0)
        assert "timeout" in logger.logs[0].message
        assert logger.logs[0].level == "error"

    def test_step_skipped(self):
        logger = ExecutionLogger()
        logger.step_skipped(1, "report", "no handler")
        assert "skipped" in logger.logs[0].message

    def test_retry_attempt(self):
        logger = ExecutionLogger()
        logger.retry_attempt(1, 2, "connection error")
        assert "retry" in logger.logs[0].message.lower()

    def test_execution_started_completed(self):
        logger = ExecutionLogger()
        logger.execution_started("review")
        logger.execution_completed("success", 1.5)
        assert len(logger.logs) == 2

    def test_get_logs_for_step(self):
        logger = ExecutionLogger()
        logger.step_started(1, "load")
        logger.step_started(2, "aggregate")
        logger.step_completed(1, "load", 0.1)
        step1_logs = logger.get_logs_for_step(1)
        assert len(step1_logs) == 2

    def test_logs_property(self):
        logger = ExecutionLogger()
        logger.info("msg1")
        logger.info("msg2")
        assert len(logger.logs) == 2
