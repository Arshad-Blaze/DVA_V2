"""Tests for progress tracking."""

import time

import pytest

from dav_platform.core.contracts import ExecutionState
from dav_platform.operations.progress import ProgressTracker


class TestProgressTracker:
    def test_initial_progress(self):
        tracker = ProgressTracker(total_steps=5)
        progress = tracker.get_progress()
        assert progress.total_steps == 5
        assert progress.current_step == 0
        assert progress.progress_percent == 0.0

    def test_start(self):
        tracker = ProgressTracker(total_steps=5)
        tracker.start()
        progress = tracker.get_progress()
        assert progress.state == ExecutionState.RUNNING

    def test_update_step(self):
        tracker = ProgressTracker(total_steps=5)
        tracker.start()
        tracker.update_step(2, "aggregate")
        progress = tracker.get_progress()
        assert progress.current_step == 2
        assert "aggregate" in progress.current_action

    def test_complete_step(self):
        tracker = ProgressTracker(total_steps=5)
        tracker.start()
        tracker.complete_step(1, 0.5)
        progress = tracker.get_progress()
        assert progress.elapsed_seconds >= 0

    def test_progress_percent(self):
        tracker = ProgressTracker(total_steps=10)
        tracker.start()
        tracker.update_step(5, "test")
        progress = tracker.get_progress()
        assert progress.progress_percent == 50.0

    def test_progress_capped_at_100(self):
        tracker = ProgressTracker(total_steps=2)
        tracker.start()
        tracker.update_step(5, "test")
        progress = tracker.get_progress()
        assert progress.progress_percent == 100.0

    def test_finish(self):
        tracker = ProgressTracker(total_steps=5)
        tracker.start()
        tracker.finish()
        progress = tracker.get_progress()
        assert progress.state == ExecutionState.COMPLETED

    def test_add_warning(self):
        tracker = ProgressTracker(total_steps=5)
        tracker.add_warning("test warning")
        progress = tracker.get_progress()
        assert "test warning" in progress.warnings

    def test_messages(self):
        tracker = ProgressTracker(total_steps=5)
        tracker.start()
        tracker.update_step(1, "load")
        tracker.update_step(2, "aggregate")
        progress = tracker.get_progress()
        assert len(progress.messages) == 2
