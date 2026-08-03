"""Execution state management."""

from dav_platform.core.contracts import ExecutionState


class StateManager:
    """Manages execution state transitions.

    Enforces valid state transitions and tracks current state.
    """

    VALID_TRANSITIONS = {
        ExecutionState.PENDING: {ExecutionState.RUNNING, ExecutionState.CANCELLED, ExecutionState.SKIPPED},
        ExecutionState.RUNNING: {ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED},
        ExecutionState.COMPLETED: set(),
        ExecutionState.SKIPPED: set(),
        ExecutionState.FAILED: {ExecutionState.RUNNING},  # allow retry
        ExecutionState.CANCELLED: set(),
    }

    def __init__(self):
        self._state = ExecutionState.PENDING
        self._history = [(ExecutionState.PENDING,)]

    @property
    def state(self) -> ExecutionState:
        return self._state

    def transition(self, new_state: ExecutionState) -> bool:
        """Attempt state transition.

        Returns True if transition was valid, False otherwise.
        """
        if new_state == self._state:
            return True

        valid = self.VALID_TRANSITIONS.get(self._state, set())
        if new_state in valid:
            self._state = new_state
            self._history.append((self._state,))
            return True
        return False

    def reset(self):
        """Reset to pending state."""
        self._state = ExecutionState.PENDING
        self._history = [(ExecutionState.PENDING,)]

    @property
    def is_terminal(self) -> bool:
        """Check if current state is terminal (no further transitions possible)."""
        return self._state in (
            ExecutionState.COMPLETED,
            ExecutionState.CANCELLED,
        )

    @property
    def history(self):
        return list(self._history)
