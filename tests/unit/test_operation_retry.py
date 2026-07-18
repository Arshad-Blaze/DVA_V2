"""Tests for retry policy."""

import pytest

from dav_platform.operations.retry import RetryPolicy, RetryState


class TestRetryPolicy:
    def test_should_retry_within_limit(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(0)
        assert policy.should_retry(1)
        assert policy.should_retry(2)

    def test_should_not_retry_at_limit(self):
        policy = RetryPolicy(max_retries=3)
        assert not policy.should_retry(3)

    def test_should_not_retry_beyond_limit(self):
        policy = RetryPolicy(max_retries=3)
        assert not policy.should_retry(5)

    def test_should_not_retry_on_non_retryable(self):
        policy = RetryPolicy(max_retries=3, retry_on=(ValueError,))
        assert policy.should_retry(0, ValueError("test"))
        assert not policy.should_retry(0, TypeError("test"))

    def test_get_delay_base(self):
        policy = RetryPolicy(delay_seconds=1.0, backoff_multiplier=2.0)
        assert policy.get_delay(0) == 1.0
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 4.0

    def test_get_delay_custom(self):
        policy = RetryPolicy(delay_seconds=0.5, backoff_multiplier=3.0)
        assert policy.get_delay(0) == 0.5
        assert policy.get_delay(1) == 1.5


class TestRetryState:
    def test_initial_state(self):
        rs = RetryState()
        assert rs.attempt == 0
        assert rs.history == []

    def test_record_failed_attempt(self):
        rs = RetryState()
        rs.record_attempt(False, "error", 1.0)
        assert rs.attempt == 1
        assert len(rs.history) == 1
        assert rs.history[0]["success"] is False

    def test_record_successful_attempt(self):
        rs = RetryState()
        rs.record_attempt(True)
        assert rs.attempt == 0  # doesn't increment on success
        assert len(rs.history) == 1

    def test_multiple_failed_attempts(self):
        rs = RetryState()
        rs.record_attempt(False, "err1")
        rs.record_attempt(False, "err2")
        rs.record_attempt(False, "err3")
        assert rs.attempt == 3
