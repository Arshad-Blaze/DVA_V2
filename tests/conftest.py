"""Root test configuration and shared fixtures for DVA Platform V2."""

import os
import sys
import tempfile
from pathlib import Path

import pytest
import polars as pl

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Sample Data Factories
# ============================================================================

@pytest.fixture
def sample_delimited_data():
    """Minimal delimited file content."""
    return "STORE|UPC|UNITS|PRICE\n1001|123456|10|9.99\n1002|789012|20|19.99\n1003|345678|30|29.99"


@pytest.fixture
def sample_fixed_width_data():
    """Minimal fixed-width file content."""
    return "H001RECORD TYPE A                                     20260101\nD1001  12345610    9.99\nD1002  78901220   19.99\nT003RECORD COUNT 000002"


@pytest.fixture
def sample_multiline_data():
    """Minimal multiline file content."""
    return "H001|20260101\nD1001|123456|10|9.99\nD1002|789012|20|19.99\nT002"


@pytest.fixture
def sample_dataframe():
    """Minimal polars DataFrame."""
    return pl.DataFrame({
        "STORE_NUM": ["1001", "1002", "1003"],
        "UPC_CODE": ["123456", "789012", "345678"],
        "UNITS": ["10", "20", "30"],
        "PRICE": ["9.99", "19.99", "29.99"],
    })


@pytest.fixture
def large_dataframe():
    """Large DataFrame for performance testing (100k rows)."""
    return pl.DataFrame({
        "store": [f"S{i:04d}" for i in range(100_000)],
        "upc": [f"{i:06d}" for i in range(100_000)],
        "units": [i % 100 + 1 for i in range(100_000)],
        "price": [round(1.0 + (i % 50) * 0.5, 2) for i in range(100_000)],
    })


# ============================================================================
# Canonical Dataset Factories
# ============================================================================

@pytest.fixture
def canonical_dataset_with_data(sample_dataframe):
    """CanonicalDataset with a real DataFrame."""
    from dav_platform.core.contracts import CanonicalDataset, CanonicalMetadata
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=["store", "upc", "units", "price"],
        metadata=CanonicalMetadata(
            total_rows=3,
            mapped_columns=4,
            quantity_column="units",
            quantity_type="units",
            confidence=0.9,
        ),
        dataframe=sample_dataframe.rename({
            "STORE_NUM": "store",
            "UPC_CODE": "upc",
            "UNITS": "units",
            "PRICE": "price",
        }),
    )


@pytest.fixture
def canonical_dataset_no_data():
    """CanonicalDataset without a DataFrame."""
    from dav_platform.core.contracts import CanonicalDataset, CanonicalMetadata
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=["store", "upc", "units", "price"],
        metadata=CanonicalMetadata(total_rows=0),
    )


@pytest.fixture
def operation_context_basic():
    """Basic OperationContext for testing."""
    from dav_platform.core.contracts import OperationContext, ExecutionStep
    return OperationContext(
        mode="AGGREGATE_AND_CALCULATE",
        session_id="test-session-001",
        execution_plan=[
            ExecutionStep(step_number=1, action="load", description="Load data"),
            ExecutionStep(step_number=2, action="validate", description="Validate data"),
            ExecutionStep(step_number=3, action="preview", description="Preview data"),
            ExecutionStep(step_number=4, action="aggregate", description="Aggregate data"),
            ExecutionStep(step_number=5, action="calculate", description="Calculate metrics"),
            ExecutionStep(step_number=6, action="summary", description="Generate summary"),
            ExecutionStep(step_number=7, action="report", description="Generate report"),
        ],
        recommended_workflow="aggregate_calculate_report",
        required_inputs=["dataset", "context"],
    )


# ============================================================================
# Mock Factories
# ============================================================================

@pytest.fixture
def mock_handler():
    """Factory for mock operation handlers."""
    def _make(return_value="ok", should_fail=False, error_msg="simulated failure"):
        def handler(step=None, dataset=None, context=None, options=None):
            if should_fail:
                raise RuntimeError(error_msg)
            return return_value
        return handler
    return _make


@pytest.fixture
def tmp_csv_file(tmp_path):
    """Factory that writes content to a temp CSV file."""
    def _make(content: str, filename: str = "test.csv"):
        p = tmp_path / filename
        p.write_text(content)
        return str(p)
    return _make
