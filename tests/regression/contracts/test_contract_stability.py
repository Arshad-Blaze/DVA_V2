"""Contract stability tests.

Verify all public contracts remain backward-compatible:
- Classes exist and are importable
- All fields exist with correct default values
- All properties work
- Instances can be created with defaults and custom values
- Dataclass instances support equality comparison
"""

import inspect
from abc import ABC
from enum import Enum

import pytest
import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ColumnMapping,
    DiscoveryResult,
    EncodingType,
    ExecutionMetadata,
    ExecutionResult,
    ExecutionState,
    FileType,
    IDataSource,
    OperationContext,
    OperationLog,
    ProcessingMode,
    QuantityRecommendation,
)


# ============================================================================
# IDataSource
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestIDataSourceContract:

    def test_class_exists(self):
        assert IDataSource is not None

    def test_is_abstract_base_class(self):
        assert issubclass(IDataSource, ABC)

    def test_has_all_abstract_methods(self):
        abstract_methods = IDataSource.__abstractmethods__
        expected = {
            "connect", "disconnect", "is_connected", "list_directory",
            "list_files", "read_sample", "open_stream",
            "download_if_required", "exists", "stat", "get_file_size",
            "directory_summary", "get_server_info", "get_connection_string",
        }
        assert expected.issubset(abstract_methods)

    def test_supports_direct_path_exists(self):
        assert hasattr(IDataSource, "supports_direct_path")

    def test_supports_direct_path_default_false(self):
        class StubSource(IDataSource):
            def connect(self): return True
            def disconnect(self): pass
            def is_connected(self): return False
            def list_directory(self, path): return []
            def list_files(self, path): return []
            def read_sample(self, path, n=100): return ""
            def open_stream(self, path): return None
            def download_if_required(self, path): return path
            def exists(self, path): return False
            def stat(self, path): return {}
            def get_file_size(self, path): return 0
            def directory_summary(self, path): return None
            def get_server_info(self): return {}
            def get_connection_string(self): return ""

        src = StubSource()
        assert src.supports_direct_path is False

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            IDataSource()


# ============================================================================
# DiscoveryResult
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestDiscoveryResultContract:

    def test_class_exists(self):
        assert DiscoveryResult is not None

    def test_is_dataclass(self):
        assert hasattr(DiscoveryResult, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "file_path", "file_type", "delimiter", "encoding",
            "has_header", "columns",
            "candidate_store", "candidate_upc", "candidate_units",
            "candidate_price", "quantity_recommendation", "confidence",
            "warnings", "raw_preview", "flatten_preview",
            "canonical_preview",
        }
        actual = set(DiscoveryResult.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_create_with_defaults(self):
        dr = DiscoveryResult(file_path="test.csv", file_type=FileType.DELIMITED)
        assert dr.file_path == "test.csv"
        assert dr.file_type == FileType.DELIMITED
        assert dr.delimiter is None
        assert dr.encoding == "utf-8"
        assert dr.has_header is False
        assert dr.columns == []
        assert dr.candidate_store == []
        assert dr.candidate_upc == []
        assert dr.candidate_units == []
        assert dr.candidate_price == []
        assert dr.quantity_recommendation is None
        assert dr.confidence == 0.0
        assert dr.warnings == []
        assert dr.raw_preview is None
        assert dr.flatten_preview is None
        assert dr.canonical_preview is None

    def test_create_with_custom_values(self):
        df = pl.DataFrame({"a": [1]})
        qr = QuantityRecommendation(recommended_column="qty", confidence=0.9)
        dr = DiscoveryResult(
            file_path="x.csv",
            file_type=FileType.EXCEL,
            delimiter="|",
            encoding="latin-1",
            has_header=True,
            columns=["col1", "col2"],
            candidate_store=[],
            candidate_upc=[],
            candidate_units=[],
            candidate_price=[],
            quantity_recommendation=qr,
            confidence=0.85,
            warnings=["warn1"],
            raw_preview=df,
            flatten_preview=df,
            canonical_preview=df,
        )
        assert dr.file_path == "x.csv"
        assert dr.file_type == FileType.EXCEL
        assert dr.delimiter == "|"
        assert dr.encoding == "latin-1"
        assert dr.has_header is True
        assert dr.quantity_recommendation.confidence == 0.9
        assert dr.confidence == 0.85
        assert dr.warnings == ["warn1"]
        assert dr.raw_preview.shape == (1, 1)

    def test_equality(self):
        a = DiscoveryResult(file_path="a.csv", file_type=FileType.DELIMITED)
        b = DiscoveryResult(file_path="a.csv", file_type=FileType.DELIMITED)
        assert a == b

    def test_inequality(self):
        a = DiscoveryResult(file_path="a.csv", file_type=FileType.DELIMITED)
        b = DiscoveryResult(file_path="b.csv", file_type=FileType.DELIMITED)
        assert a != b


# ============================================================================
# CanonicalDataset
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestCanonicalDatasetContract:

    def test_class_exists(self):
        assert CanonicalDataset is not None

    def test_is_dataclass(self):
        assert hasattr(CanonicalDataset, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "file_path", "physical_to_canonical", "canonical_columns",
            "column_mappings", "dataframe", "metadata", "warnings",
            "recommendations",
        }
        actual = set(CanonicalDataset.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_has_df_property(self):
        assert hasattr(CanonicalDataset, "df")

    def test_has_row_count_property(self):
        assert hasattr(CanonicalDataset, "row_count")

    def test_has_column_count_property(self):
        assert hasattr(CanonicalDataset, "column_count")

    def test_has_resolved_quantity_column_property(self):
        assert hasattr(CanonicalDataset, "resolved_quantity_column")

    def test_create_with_defaults(self):
        ds = CanonicalDataset()
        assert ds.file_path == ""
        assert ds.physical_to_canonical == {}
        assert ds.canonical_columns == []
        assert ds.column_mappings == []
        assert ds.dataframe is None
        assert ds.metadata is None
        assert ds.warnings == []
        assert ds.recommendations == []

    def test_df_property_returns_dataframe(self):
        df = pl.DataFrame({"a": [1, 2]})
        ds = CanonicalDataset(dataframe=df)
        assert ds.df is df

    def test_df_property_none_when_no_data(self):
        ds = CanonicalDataset()
        assert ds.df is None

    def test_row_count_with_data(self):
        df = pl.DataFrame({"a": [1, 2, 3]})
        ds = CanonicalDataset(dataframe=df)
        assert ds.row_count == 3

    def test_row_count_without_data(self):
        ds = CanonicalDataset()
        assert ds.row_count == 0

    def test_column_count_with_data(self):
        df = pl.DataFrame({"a": [1], "b": [2], "c": [3]})
        ds = CanonicalDataset(dataframe=df)
        assert ds.column_count == 3

    def test_column_count_without_data(self):
        ds = CanonicalDataset()
        assert ds.column_count == 0

    def test_resolved_quantity_column_with_metadata(self):
        meta = CanonicalMetadata(quantity_column="units")
        ds = CanonicalDataset(metadata=meta)
        assert ds.resolved_quantity_column == "units"

    def test_resolved_quantity_column_without_metadata(self):
        ds = CanonicalDataset()
        assert ds.resolved_quantity_column is None

    def test_create_with_custom_values(self):
        df = pl.DataFrame({"store": ["S1"]})
        meta = CanonicalMetadata(total_rows=1, quantity_column="units")
        ds = CanonicalDataset(
            file_path="/data.csv",
            physical_to_canonical={"STORE": "store"},
            canonical_columns=["store"],
            dataframe=df,
            metadata=meta,
            warnings=["w1"],
            recommendations=["r1"],
        )
        assert ds.file_path == "/data.csv"
        assert ds.physical_to_canonical == {"STORE": "store"}
        assert ds.row_count == 1

    def test_equality(self):
        a = CanonicalDataset(file_path="x.csv")
        b = CanonicalDataset(file_path="x.csv")
        assert a == b

    def test_inequality(self):
        a = CanonicalDataset(file_path="x.csv")
        b = CanonicalDataset(file_path="y.csv")
        assert a != b


# ============================================================================
# CanonicalMetadata
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestCanonicalMetadataContract:

    def test_class_exists(self):
        assert CanonicalMetadata is not None

    def test_is_dataclass(self):
        assert hasattr(CanonicalMetadata, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "total_rows", "mapped_columns", "unmapped_columns",
            "quantity_column", "quantity_type", "confidence",
            "source_file_type", "encoding", "flatten_strategy",
            "uom_strategy", "validation_summary", "ignored_columns",
            "warnings", "transformation_log",
        }
        actual = set(CanonicalMetadata.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_create_with_defaults(self):
        m = CanonicalMetadata()
        assert m.total_rows == 0
        assert m.mapped_columns == 0
        assert m.unmapped_columns == 0
        assert m.quantity_column is None
        assert m.quantity_type == "none"
        assert m.confidence == 0.0
        assert m.source_file_type == ""
        assert m.encoding == "utf-8"
        assert m.flatten_strategy == "none"
        assert m.uom_strategy == "none"
        assert m.validation_summary is None
        assert m.ignored_columns == []
        assert m.warnings == []
        assert m.transformation_log == []

    def test_create_with_custom_values(self):
        m = CanonicalMetadata(
            total_rows=100,
            mapped_columns=5,
            unmapped_columns=2,
            quantity_column="qty",
            quantity_type="weighted_qty",
            confidence=0.92,
            source_file_type="delimited",
            encoding="latin-1",
            flatten_strategy="hierarchy",
            uom_strategy="detected",
            validation_summary={"errors": 0},
            ignored_columns=["col1"],
            warnings=["w1"],
            transformation_log=["log1"],
        )
        assert m.total_rows == 100
        assert m.quantity_type == "weighted_qty"
        assert m.flatten_strategy == "hierarchy"
        assert m.uom_strategy == "detected"

    def test_equality(self):
        a = CanonicalMetadata(total_rows=50)
        b = CanonicalMetadata(total_rows=50)
        assert a == b

    def test_inequality(self):
        a = CanonicalMetadata(total_rows=50)
        b = CanonicalMetadata(total_rows=100)
        assert a != b


# ============================================================================
# OperationContext
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestOperationContextContract:

    def test_class_exists(self):
        assert OperationContext is not None

    def test_is_dataclass(self):
        assert hasattr(OperationContext, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "mode", "options", "session_id", "metadata",
            "business_goal", "capability_matrix", "execution_plan",
            "recommended_workflow", "required_inputs", "missing_inputs",
            "expected_outputs", "warnings", "confidence",
        }
        actual = set(OperationContext.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_create_with_defaults(self):
        ctx = OperationContext()
        assert ctx.mode == ProcessingMode.AGGREGATE_ONLY
        assert ctx.options == {}
        assert ctx.session_id == ""
        assert ctx.metadata == {}
        assert ctx.business_goal is None
        assert ctx.capability_matrix is None
        assert ctx.execution_plan == []
        assert ctx.recommended_workflow == ""
        assert ctx.required_inputs == []
        assert ctx.missing_inputs == []
        assert ctx.expected_outputs == []
        assert ctx.warnings == []
        assert ctx.confidence == 0.0

    def test_create_with_custom_values(self):
        from dav_platform.core.contracts import BusinessGoal, CapabilityMatrix, ExecutionStep
        cm = CapabilityMatrix(can_aggregate=True)
        ctx = OperationContext(
            mode=ProcessingMode.AGGREGATE_AND_CALCULATE,
            options={"key": "val"},
            session_id="s1",
            metadata={"m": 1},
            business_goal=BusinessGoal.AGGREGATION,
            capability_matrix=cm,
            execution_plan=[ExecutionStep(step_number=1, action="load", description="Load")],
            recommended_workflow="load_agg",
            required_inputs=["dataset"],
            missing_inputs=["extra"],
            expected_outputs=["report"],
            warnings=["w"],
            confidence=0.75,
        )
        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert ctx.business_goal == BusinessGoal.AGGREGATION
        assert ctx.capability_matrix.can_aggregate is True
        assert len(ctx.execution_plan) == 1
        assert ctx.confidence == 0.75

    def test_equality(self):
        a = OperationContext(session_id="x")
        b = OperationContext(session_id="x")
        assert a == b

    def test_inequality(self):
        a = OperationContext(session_id="x")
        b = OperationContext(session_id="y")
        assert a != b


# ============================================================================
# ExecutionResult
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestExecutionResultContract:

    def test_class_exists(self):
        assert ExecutionResult is not None

    def test_is_dataclass(self):
        assert hasattr(ExecutionResult, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "state", "step_results", "metadata", "logs",
            "warnings", "errors",
        }
        actual = set(ExecutionResult.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_has_succeeded_property(self):
        assert hasattr(ExecutionResult, "succeeded")

    def test_has_failed_property(self):
        assert hasattr(ExecutionResult, "failed")

    def test_has_cancelled_property(self):
        assert hasattr(ExecutionResult, "cancelled")

    def test_create_with_defaults(self):
        r = ExecutionResult()
        assert r.state == ExecutionState.PENDING
        assert r.step_results == []
        assert r.metadata is None
        assert r.logs == []
        assert r.warnings == []
        assert r.errors == []

    def test_succeeded_true_when_completed(self):
        r = ExecutionResult(state=ExecutionState.COMPLETED)
        assert r.succeeded is True
        assert r.failed is False
        assert r.cancelled is False

    def test_failed_true_when_failed(self):
        r = ExecutionResult(state=ExecutionState.FAILED)
        assert r.succeeded is False
        assert r.failed is True
        assert r.cancelled is False

    def test_cancelled_true_when_cancelled(self):
        r = ExecutionResult(state=ExecutionState.CANCELLED)
        assert r.succeeded is False
        assert r.failed is False
        assert r.cancelled is True

    def test_succeeded_false_when_pending(self):
        r = ExecutionResult(state=ExecutionState.PENDING)
        assert r.succeeded is False
        assert r.failed is False
        assert r.cancelled is False

    def test_succeeded_false_when_running(self):
        r = ExecutionResult(state=ExecutionState.RUNNING)
        assert r.succeeded is False
        assert r.failed is False
        assert r.cancelled is False

    def test_succeeded_false_when_skipped(self):
        r = ExecutionResult(state=ExecutionState.SKIPPED)
        assert r.succeeded is False
        assert r.failed is False
        assert r.cancelled is False

    def test_create_with_custom_values(self):
        from dav_platform.core.contracts import ExecutionMetadata, ExecutionStepResult
        meta = ExecutionMetadata(workflow="w1", total_steps=3)
        step = ExecutionStepResult(step_number=1, action="load", state=ExecutionState.COMPLETED)
        r = ExecutionResult(
            state=ExecutionState.COMPLETED,
            step_results=[step],
            metadata=meta,
            logs=[],
            warnings=["w1"],
            errors=[],
        )
        assert r.state == ExecutionState.COMPLETED
        assert len(r.step_results) == 1
        assert r.metadata.workflow == "w1"

    def test_equality(self):
        a = ExecutionResult(state=ExecutionState.COMPLETED)
        b = ExecutionResult(state=ExecutionState.COMPLETED)
        assert a == b

    def test_inequality(self):
        a = ExecutionResult(state=ExecutionState.COMPLETED)
        b = ExecutionResult(state=ExecutionState.FAILED)
        assert a != b


# ============================================================================
# ExecutionMetadata
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestExecutionMetadataContract:

    def test_class_exists(self):
        assert ExecutionMetadata is not None

    def test_is_dataclass(self):
        assert hasattr(ExecutionMetadata, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "workflow", "total_steps", "completed_steps",
            "failed_steps", "skipped_steps", "execution_duration",
            "warnings", "errors", "outcome",
        }
        actual = set(ExecutionMetadata.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_create_with_defaults(self):
        m = ExecutionMetadata()
        assert m.workflow == ""
        assert m.total_steps == 0
        assert m.completed_steps == 0
        assert m.failed_steps == 0
        assert m.skipped_steps == 0
        assert m.execution_duration == 0.0
        assert m.warnings == []
        assert m.errors == []
        assert m.outcome == ""

    def test_create_with_custom_values(self):
        m = ExecutionMetadata(
            workflow="pipeline",
            total_steps=5,
            completed_steps=4,
            failed_steps=1,
            skipped_steps=0,
            execution_duration=12.5,
            warnings=["w1"],
            errors=["e1"],
            outcome="partial",
        )
        assert m.workflow == "pipeline"
        assert m.total_steps == 5
        assert m.execution_duration == 12.5
        assert m.outcome == "partial"

    def test_equality(self):
        a = ExecutionMetadata(workflow="w")
        b = ExecutionMetadata(workflow="w")
        assert a == b

    def test_inequality(self):
        a = ExecutionMetadata(workflow="a")
        b = ExecutionMetadata(workflow="b")
        assert a != b


# ============================================================================
# OperationLog
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestOperationLogContract:

    def test_class_exists(self):
        assert OperationLog is not None

    def test_is_dataclass(self):
        assert hasattr(OperationLog, "__dataclass_fields__")

    def test_has_all_fields(self):
        expected_fields = {
            "timestamp", "level", "step_number", "action",
            "message", "duration_seconds", "metadata",
        }
        actual = set(OperationLog.__dataclass_fields__.keys())
        assert expected_fields.issubset(actual)

    def test_create_with_defaults(self):
        log = OperationLog()
        assert log.timestamp == ""
        assert log.level == "info"
        assert log.step_number is None
        assert log.action == ""
        assert log.message == ""
        assert log.duration_seconds == 0.0
        assert log.metadata == {}

    def test_create_with_custom_values(self):
        log = OperationLog(
            timestamp="2026-01-01T00:00:00",
            level="error",
            step_number=3,
            action="validate",
            message="validation failed",
            duration_seconds=1.23,
            metadata={"key": "val"},
        )
        assert log.timestamp == "2026-01-01T00:00:00"
        assert log.level == "error"
        assert log.step_number == 3
        assert log.action == "validate"
        assert log.message == "validation failed"
        assert log.duration_seconds == 1.23
        assert log.metadata == {"key": "val"}

    def test_equality(self):
        a = OperationLog(message="x")
        b = OperationLog(message="x")
        assert a == b

    def test_inequality(self):
        a = OperationLog(message="x")
        b = OperationLog(message="y")
        assert a != b


# ============================================================================
# ExecutionState
# ============================================================================

@pytest.mark.contract
@pytest.mark.regression
class TestExecutionStateContract:

    def test_class_exists(self):
        assert ExecutionState is not None

    def test_is_enum(self):
        assert issubclass(ExecutionState, Enum)

    def test_has_pending(self):
        assert ExecutionState.PENDING.value == "pending"

    def test_has_running(self):
        assert ExecutionState.RUNNING.value == "running"

    def test_has_completed(self):
        assert ExecutionState.COMPLETED.value == "completed"

    def test_has_skipped(self):
        assert ExecutionState.SKIPPED.value == "skipped"

    def test_has_failed(self):
        assert ExecutionState.FAILED.value == "failed"

    def test_has_cancelled(self):
        assert ExecutionState.CANCELLED.value == "cancelled"

    def test_all_six_members(self):
        members = list(ExecutionState)
        assert len(members) == 6

    def test_member_names(self):
        names = {s.name for s in ExecutionState}
        assert names == {
            "PENDING", "RUNNING", "COMPLETED",
            "SKIPPED", "FAILED", "CANCELLED",
        }
