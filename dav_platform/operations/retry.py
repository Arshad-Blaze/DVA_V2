"""Retry policy for step execution."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RetryPolicy:
    """Configurable retry policy."""
    max_retries: int = 3
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    retry_on: tuple = (Exception,)  # exception types to retry on

    def should_retry(self, attempt: int, error: Optional[Exception] = None) -> bool:
        """Check if retry should be attempted.

        Args:
            attempt: Current attempt number (0-based)
            error: Exception that caused failure

        Returns:
            True if retry should be attempted
        """
        if attempt >= self.max_retries:
            return False

        if error is not None and not isinstance(error, self.retry_on):
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """Get delay before next retry attempt.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        return self.delay_seconds * (self.backoff_multiplier ** attempt)


@dataclass
class RetryState:
    """Tracks retry state for a step."""
    attempt: int = 0
    history: list = field(default_factory=list)

    def record_attempt(self, success: bool, error: Optional[str] = None, delay: float = 0.0):
        """Record a retry attempt."""
        self.history.append({
            "attempt": self.attempt,
            "success": success,
            "error": error,
            "delay": delay,
        })
        if not success:
            self.attempt += 1
