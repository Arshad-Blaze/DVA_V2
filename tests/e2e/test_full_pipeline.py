"""End-to-end tests for the full Discovery → Canonical → Requirement → Operation pipeline."""

import pytest
import polars as pl

from dav_platform.core.contracts import (
    CandidateMapping,
    CanonicalDataset,
    CanonicalMetadata,
    DiscoveryResult,
    ExecutionResult,
    ExecutionState,
    FileType,
    OperationContext,
    ProcessingMode,
)
from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.requirements.engine import RequirementLayer
from dav_platform.operations.engine import OperationEngine
from dav_platform.operations.dispatcher import register_handler, clear_handlers


def _make_handler(name):
    def handler(step, dataset=None, context=None, options=None):
        return {"action": name, "step": step.step_number}
    return handler


def _make_failing_handler(name):
    def handler(step, dataset=None, context=None, options=None):
        raise RuntimeError(f"Simulated failure in {name}")
    return handler


def _build_discovery_delimited(
    delimiter="|",
    columns=None,
    store_col="STORE_NUM",
    upc_col="UPC_CODE",
    units_col="UNITS",
    price_col="PRICE",
):
    columns = columns or ["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"]
    return DiscoveryResult(
        file_path="/data/retailer.txt",
        file_type=FileType.DELIMITED,
        delimiter=delimiter,
        delimiter_confidence=0.99,
        encoding="utf-8",
        has_header=True,
        header_confidence=0.95,
        columns=columns,
        candidate_store=[CandidateMapping(physical_column=store_col, confidence=0.95)],
        candidate_upc=[CandidateMapping(physical_column=upc_col, confidence=0.95)],
        candidate_units=[CandidateMapping(physical_column=units_col, confidence=0.90)],
        candidate_price=[CandidateMapping(physical_column=price_col, confidence=0.90)],
        confidence=0.92,
    )


def _build_discovery_fixed_width():
    return DiscoveryResult(
        file_path="/data/retailer_fw.txt",
        file_type=FileType.FIXED_WIDTH,
        encoding="utf-8",
        has_header=True,
        header_confidence=0.90,
        columns=["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"],
        candidate_store=[CandidateMapping(physical_column="STORE_NUM", confidence=0.92)],
        candidate_upc=[CandidateMapping(physical_column="UPC_CODE", confidence=0.92)],
        candidate_units=[CandidateMapping(physical_column="UNITS", confidence=0.88)],
        candidate_price=[CandidateMapping(physical_column="PRICE", confidence=0.88)],
        confidence=0.90,
    )


def _build_discovery_multiline():
    return DiscoveryResult(
        file_path="/data/retailer_ml.txt",
        file_type=FileType.DELIMITED,
        delimiter="|",
        delimiter_confidence=0.95,
        encoding="utf-8",
        has_header=True,
        header_confidence=0.90,
        is_multiline=True,
        columns=["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"],
        candidate_store=[CandidateMapping(physical_column="STORE_NUM", confidence=0.90)],
        candidate_upc=[CandidateMapping(physical_column="UPC_CODE", confidence=0.90)],
        candidate_units=[CandidateMapping(physical_column="UNITS", confidence=0.85)],
        candidate_price=[CandidateMapping(physical_column="PRICE", confidence=0.85)],
        confidence=0.88,
    )


def _build_dataframe_delimited(n=5):
    return pl.DataFrame({
        "STORE_NUM": [f"S{i:03d}" for i in range(n)],
        "UPC_CODE": [f"0001234567890{i}" for i in range(n)],
        "UNITS": [10 + i for i in range(n)],
        "PRICE": [1.99 + i * 0.50 for i in range(n)],
    })


def _build_dataframe_fixed_width(n=3):
    return pl.DataFrame({
        "STORE_NUM": [f"S{i:03d}" for i in range(n)],
        "UPC_CODE": [f"0001234567890{i}" for i in range(n)],
        "UNITS": [5 + i for i in range(n)],
        "PRICE": [2.50 + i * 0.75 for i in range(n)],
    })


def _run_full_pipeline(discovery, dataframe, mode=None, options=None):
    canonical_engine = CanonicalEngine()
    dataset = canonical_engine.transform(discovery, data=dataframe)

    requirement_layer = RequirementLayer()
    context = requirement_layer.process(dataset=dataset, mode=mode, options=options)

    return dataset, context


def _get_handler_actions_for_context(context):
    workflow = context.recommended_workflow
    action_map = {
        "aggregate_calculate_report": ["load", "validate", "aggregate", "calculate", "summary", "report"],
        "aggregate_report": ["load", "validate", "aggregate", "summary", "report"],
        "review": ["load", "preview", "summary"],
    }
    return action_map.get(workflow, ["load", "preview", "summary"])


# ============================================================================
# Test Classes
# ============================================================================


class TestDelimitedRetailerPipeline:
    @pytest.mark.e2e
    def test_pipe_delimited_full_pipeline(self):
        discovery = _build_discovery_delimited(delimiter="|")
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        assert dataset is not None
        assert dataset.row_count == 5
        assert context is not None
        assert isinstance(context, OperationContext)
        assert len(context.execution_plan) > 0

        actions = _get_handler_actions_for_context(context)
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert isinstance(result, ExecutionResult)
        assert result.succeeded
        assert result.metadata.total_steps == len(context.execution_plan)
        assert result.metadata.completed_steps == len(context.execution_plan)
        assert result.metadata.failed_steps == 0
        assert result.metadata.outcome == "success"

        for step_result in result.step_results:
            assert step_result.state == ExecutionState.COMPLETED
            assert step_result.result is not None

        clear_handlers()


class TestFixedWidthRetailerPipeline:
    @pytest.mark.e2e
    def test_fixed_width_full_pipeline(self):
        discovery = _build_discovery_fixed_width()
        dataframe = _build_dataframe_fixed_width(n=3)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        assert dataset is not None
        assert dataset.row_count == 3
        assert context is not None
        assert isinstance(context, OperationContext)

        actions = _get_handler_actions_for_context(context)
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert isinstance(result, ExecutionResult)
        assert result.succeeded
        assert result.metadata.outcome == "success"
        assert len(result.step_results) == len(context.execution_plan)

        clear_handlers()


class TestMultilineRetailerPipeline:
    @pytest.mark.e2e
    def test_multiline_full_pipeline(self):
        discovery = _build_discovery_multiline()
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        assert dataset is not None
        assert context is not None
        assert isinstance(context, OperationContext)

        actions = _get_handler_actions_for_context(context)
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert isinstance(result, ExecutionResult)
        assert result.succeeded
        assert result.metadata.outcome == "success"

        clear_handlers()


class TestAggregateAndCalculatePipeline:
    @pytest.mark.e2e
    def test_aggregate_and_calculate_mode(self):
        discovery = _build_discovery_delimited()
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        assert context.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert context.recommended_workflow == "aggregate_calculate_report"

        actions = ["load", "validate", "aggregate", "calculate", "summary", "report"]
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert result.succeeded
        assert result.metadata.outcome == "success"

        action_results = {sr.action: sr for sr in result.step_results}
        assert "load" in action_results
        assert "validate" in action_results
        assert "aggregate" in action_results
        assert "calculate" in action_results
        assert "summary" in action_results
        assert "report" in action_results

        assert action_results["load"].state == ExecutionState.COMPLETED
        assert action_results["validate"].state == ExecutionState.COMPLETED
        assert action_results["aggregate"].state == ExecutionState.COMPLETED
        assert action_results["calculate"].state == ExecutionState.COMPLETED

        clear_handlers()


class TestAggregateOnlyPipeline:
    @pytest.mark.e2e
    def test_aggregate_only_mode(self):
        discovery = _build_discovery_delimited()
        discovery.candidate_units = []
        discovery.candidate_weighted_qty = []
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        assert context.mode == ProcessingMode.AGGREGATE_ONLY
        assert context.recommended_workflow == "aggregate_report"

        actions = ["load", "validate", "aggregate", "summary", "report"]
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert result.succeeded
        assert result.metadata.outcome == "success"

        action_results = {sr.action: sr for sr in result.step_results}
        assert "load" in action_results
        assert "validate" in action_results
        assert "aggregate" in action_results
        assert "calculate" not in action_results

        clear_handlers()


class TestRawReviewPipeline:
    @pytest.mark.e2e
    def test_raw_review_mode(self):
        discovery = DiscoveryResult(
            file_path="/data/review.txt",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            columns=["DESCRIPTION", "ITEM_CODE", "COLOR", "SIZE"],
            confidence=0.80,
        )
        dataframe = pl.DataFrame({
            "DESCRIPTION": ["Widget A", "Widget B", "Gadget C"],
            "ITEM_CODE": ["WDG-001", "WDG-002", "GDG-001"],
            "COLOR": ["Red", "Blue", "Green"],
            "SIZE": ["S", "M", "L"],
        })

        dataset, context = _run_full_pipeline(discovery, dataframe)

        assert context.mode == ProcessingMode.RAW_REVIEW
        assert context.recommended_workflow == "review"

        actions = ["load", "preview", "summary"]
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert result.succeeded

        action_results = {sr.action: sr for sr in result.step_results}
        assert "load" in action_results
        assert "preview" in action_results
        assert "summary" in action_results
        assert "aggregate" not in action_results
        assert "calculate" not in action_results

        clear_handlers()


class TestPipelineWithFailures:
    @pytest.mark.e2e
    def test_handler_failure_reflected_in_result(self):
        discovery = _build_discovery_delimited()
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        actions = _get_handler_actions_for_context(context)
        for action in actions:
            register_handler(action, _make_handler(action))

        register_handler("aggregate", _make_failing_handler("aggregate"))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert result.failed
        assert result.metadata.outcome == "failed"
        assert result.metadata.failed_steps > 0
        assert len(result.errors) > 0

        failed_steps = [sr for sr in result.step_results if sr.state == ExecutionState.FAILED]
        assert len(failed_steps) > 0
        assert failed_steps[0].action == "aggregate"
        assert "Simulated failure" in failed_steps[0].error

        clear_handlers()

    @pytest.mark.e2e
    def test_optional_step_failure_allows_continuation(self):
        discovery = _build_discovery_delimited()
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        summary_found = False
        for step in context.execution_plan:
            if step.action == "summary" and not step.required:
                summary_found = True
                break

        if summary_found:
            register_handler("summary", _make_failing_handler("summary"))

        for action in _get_handler_actions_for_context(context):
            if action != "summary":
                register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        completed = [sr for sr in result.step_results if sr.state == ExecutionState.COMPLETED]
        assert len(completed) > 0

        clear_handlers()


class TestContextImmutability:
    @pytest.mark.e2e
    def test_operation_context_not_modified_by_operation_layer(self):
        discovery = _build_discovery_delimited()
        dataframe = _build_dataframe_delimited(n=5)

        dataset, context = _run_full_pipeline(discovery, dataframe)

        original_mode = context.mode
        original_session_id = context.session_id
        original_workflow = context.recommended_workflow
        original_plan_length = len(context.execution_plan)
        original_plan_steps = [
            (s.step_number, s.action, s.description, s.required)
            for s in context.execution_plan
        ]
        original_options = dict(context.options)
        original_metadata_keys = set(context.metadata.keys())

        actions = _get_handler_actions_for_context(context)
        for action in actions:
            register_handler(action, _make_handler(action))

        engine = OperationEngine()
        result = engine.execute(context, dataset=dataset)

        assert result.succeeded

        assert context.mode == original_mode
        assert context.session_id == original_session_id
        assert context.recommended_workflow == original_workflow
        assert len(context.execution_plan) == original_plan_length

        for i, step in enumerate(context.execution_plan):
            orig = original_plan_steps[i]
            assert step.step_number == orig[0]
            assert step.action == orig[1]
            assert step.description == orig[2]
            assert step.required == orig[3]

        assert context.options == original_options
        assert set(context.metadata.keys()) == original_metadata_keys

        clear_handlers()
