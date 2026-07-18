"""Tests for execution state management."""

import pytest

from dav_platform.core.contracts import ExecutionState
from dav_platform.operations.state import StateManager


class TestStateManager:
    def test_initial_state(self):
        sm = StateManager()
        assert sm.state == ExecutionState.PENDING

    def test_pending_to_running(self):
        sm = StateManager()
        assert sm.transition(ExecutionState.RUNNING)
        assert sm.state == ExecutionState.RUNNING

    def test_running_to_completed(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        assert sm.transition(ExecutionState.COMPLETED)
        assert sm.state == ExecutionState.COMPLETED

    def test_running_to_failed(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        assert sm.transition(ExecutionState.FAILED)
        assert sm.state == ExecutionState.FAILED

    def test_failed_to_running_retry(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        sm.transition(ExecutionState.FAILED)
        assert sm.transition(ExecutionState.RUNNING)
        assert sm.state == ExecutionState.RUNNING

    def test_pending_to_cancelled(self):
        sm = StateManager()
        assert sm.transition(ExecutionState.CANCELLED)
        assert sm.state == ExecutionState.CANCELLED

    def test_running_to_cancelled(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        assert sm.transition(ExecutionState.CANCELLED)
        assert sm.state == ExecutionState.CANCELLED

    def test_invalid_transition(self):
        sm = StateManager()
        assert not sm.transition(ExecutionState.COMPLETED)
        assert sm.state == ExecutionState.PENDING

    def test_completed_is_terminal(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        sm.transition(ExecutionState.COMPLETED)
        assert sm.is_terminal

    def test_cancelled_is_terminal(self):
        sm = StateManager()
        sm.transition(ExecutionState.CANCELLED)
        assert sm.is_terminal

    def test_pending_is_not_terminal(self):
        sm = StateManager()
        assert not sm.is_terminal

    def test_reset(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        sm.transition(ExecutionState.COMPLETED)
        sm.reset()
        assert sm.state == ExecutionState.PENDING

    def test_history(self):
        sm = StateManager()
        sm.transition(ExecutionState.RUNNING)
        sm.transition(ExecutionState.COMPLETED)
        assert len(sm.history) == 3  # pending, running, completed

    def test_same_state_transition(self):
        sm = StateManager()
        assert sm.transition(ExecutionState.PENDING)  # same state
        assert sm.state == ExecutionState.PENDING
