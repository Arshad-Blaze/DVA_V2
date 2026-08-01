"""Shared fixtures for UI service/controller tests.

Builds realistic backend DiscoveryResult and CanonicalDataset objects so
UI tests exercise the real engines via the service wiring.
"""

import polars as pl
import pytest

from dav_platform.core.contracts import (
    CandidateMapping,
    DiscoveryResult,
    FileType,
    QuantityRecommendation,
)


SALES_COLUMNS = [
    "Store", "UPC", "Description", "Brand", "Department",
    "Category", "Units_Sold", "Sales", "Date",
]


def make_discovery_result() -> DiscoveryResult:
    """A realistic Detection layer result (9 columns, delimited CSV)."""
    return DiscoveryResult(
        file_path="/data/sales_q2_2026.csv",
        file_type=FileType.DELIMITED,
        delimiter=",",
        delimiter_confidence=1.0,
        encoding="utf-8",
        encoding_confidence=1.0,
        has_header=True,
        header_confidence=1.0,
        confidence=0.95,
        columns=list(SALES_COLUMNS),
        candidate_store=[CandidateMapping(physical_column="Store", confidence=0.99)],
        candidate_upc=[CandidateMapping(physical_column="UPC", confidence=0.99)],
        candidate_description=[CandidateMapping(physical_column="Description", confidence=0.98)],
        candidate_brand=[CandidateMapping(physical_column="Brand", confidence=0.95)],
        candidate_department=[CandidateMapping(physical_column="Department", confidence=0.95)],
        candidate_category=[CandidateMapping(physical_column="Category", confidence=0.95)],
        candidate_units=[CandidateMapping(physical_column="Units_Sold", confidence=0.94)],
        candidate_sales=[CandidateMapping(physical_column="Sales", confidence=0.94)],
        candidate_date=[CandidateMapping(physical_column="Date", confidence=0.93)],
        quantity_recommendation=QuantityRecommendation(
            recommended_column="Units_Sold", recommendation_type="unit", confidence=0.9,
        ),
    )


def make_sales_dataframe(rows: int = 20) -> pl.DataFrame:
    return pl.DataFrame({
        "Store": [f"S{i:03d}" for i in range(1, rows + 1)],
        "UPC": [f"UPC{i}" for i in range(1, rows + 1)],
        "Description": [f"Desc {i}" for i in range(1, rows + 1)],
        "Brand": [f"Brand{i % 5}" for i in range(1, rows + 1)],
        "Department": [f"Dept{i % 4}" for i in range(1, rows + 1)],
        "Category": [f"Cat{i % 6}" for i in range(1, rows + 1)],
        "Units_Sold": [i * 10 for i in range(1, rows + 1)],
        "Sales": [i * 10.5 for i in range(1, rows + 1)],
        "Date": [f"2026-0{(i % 9) + 1}-{i:02d}" for i in range(1, rows + 1)],
    })


@pytest.fixture
def discovery_result() -> DiscoveryResult:
    return make_discovery_result()


@pytest.fixture
def sales_dataframe() -> pl.DataFrame:
    return make_sales_dataframe()
