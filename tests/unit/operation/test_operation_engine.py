"""Tests for Operation Engine."""

import pytest

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ExecutionResult,
    ExecutionState,
    ExecutionStep,
    OperationContext,
    ProcessingMode,
)
from dav_platform.operations.engine import OperationEngine
from dav_platform.operations.dispatcher import clear_handlers


def _make_context(workflow="review", steps=None):
    if steps is None:
        steps = [
            ExecutionStep(1, "load", "Load data", required=True, layer="operation"),
            ExecutionStep(2, "preview", "Preview data", required=False, layer="operation"),
        ]
    return OperationContext(
        mode=ProcessingMode.RAW_REVIEW,
        session_id="test-123",
        execution_plan=steps,
        recommended_workflow=workflow,
    )


def _make_dataset():
    import polars as pl
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=["store", "upc", "quantity"],
        metadata=CanonicalMetadata(total_rows=10),
        dataframe=pl.DataFrame({"store": ["1"], "upc": ["2"], "quantity": ["3"]}),
    )


class TestOperationEngine:
    def setup_method(self):
        clear_handlers()

    def teardown_method(self):
        clear_handlers()

    def test_execute_with_handlers(self):
        results = {"load": "loaded", "preview": "previewed"}

        def make_handler(key):
            def handler(step, dataset=None, context=None, options=None):
                return results[key]
            return handler

        for action in results:
            register_handler(action, make_handler(action))

        engine = OperationEngine()
        ctx = _make_context()
        result = engine.execute(ctx, dataset=_make_dataset())

        assert isinstance(result, ExecutionResult)
        assert result.succeeded
        assert len(result.step_results) == 2
        assert result.metadata.outcome == "success"

    def test_execute_missing_required_handler(self):
        # No handlers registered, all steps required
        steps = [
            ExecutionStep(1, "load", "Load", required=True),
        ]
        ctx = _make_context(steps=steps)
        engine = OperationEngine()
        result = engine.execute(ctx)

        assert result.failed

    def test_execute_missing_optional_handler_skips(self):
        steps = [
            ExecutionStep(1, "load", "Load", required=True),
            ExecutionStep(2, "report", "Report", required=False),
        ]
        ctx = _make_context(steps=steps)

        def load_handler(step, dataset=None, context=None, options=None):
            return "loaded"

        register_handler("load", load_handler)

        engine = OperationEngine()
        result = engine.execute(ctx)

        assert result.succeeded
        # load completed, report skipped
        assert result.step_results[0].state == ExecutionState.COMPLETED
        assert result.step_results[1].state == ExecutionState.SKIPPED

    def test_execute_cancellation(self):
        def slow_handler(step, dataset=None, context=None, options=None):
            import time
            time.sleep(0.1)
            return "done"

        register_handler("load", slow_handler)
        register_handler("preview", slow_handler)

        steps = [
            ExecutionStep(1, "load", "Load", required=True),
            ExecutionStep(2, "preview", "Preview", required=True),
        ]
        ctx = _make_context(steps=steps)

        engine = OperationEngine()
        engine.cancel()  # Cancel before executing
        result = engine.execute(ctx)

        assert result.cancelled

    def test_execute_metadata(self):
        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        register_handler("load", handler)
        register_handler("preview", handler)

        ctx = _make_context()
        engine = OperationEngine()
        result = engine.execute(ctx, dataset=_make_dataset())

        assert result.metadata is not None
        assert result.metadata.total_steps == 2
        assert result.metadata.completed_steps == 2
        assert result.metadata.failed_steps == 0
        assert result.metadata.workflow == "review"

    def test_execute_logs(self):
        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        register_handler("load", handler)
        register_handler("preview", handler)

        ctx = _make_context()
        engine = OperationEngine()
        result = engine.execute(ctx, dataset=_make_dataset())

        assert len(result.logs) > 0
        # Should have execution_started, step_started, step_completed (x2), execution_completed
        assert any("started" in l.message for l in result.logs)

    def test_execute_with_dataset(self):
        def handler(step, dataset=None, context=None, options=None):
            return dataset.row_count if dataset else 0

        register_handler("load", handler)

        ds = _make_dataset()
        ctx = _make_context(steps=[
            ExecutionStep(1, "load", "Load", required=True),
        ])
        engine = OperationEngine()
        result = engine.execute(ctx, dataset=ds)

        assert result.succeeded
        assert result.step_results[0].result == ds.row_count

    def test_execute_progress(self):
        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        for action in ["load", "preview"]:
            register_handler(action, handler)

        ctx = _make_context()
        engine = OperationEngine()
        result = engine.execute(ctx)

        assert result.metadata.execution_duration >= 0


# Need to import register_handler
from dav_platform.operations.dispatcher import register_handler
