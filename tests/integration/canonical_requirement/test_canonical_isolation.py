"""Integration tests: Canonical layer isolation — NO physical schema leakage.

Verifies that CanonicalDataset + CanonicalMetadata expose ONLY business-meaningful
information. No downstream layer should know about physical columns, layouts,
delimiters, record types, fixed-width structures, or multiline structures.
"""

import pytest
import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.core.contracts import (
    CANONICAL_COLUMNS,
    CandidateMapping,
    CanonicalDataset,
    CanonicalMetadata,
    DetectionStatistics,
    DiscoveryResult,
    FileType,
    LayoutField,
    RecordTypeInfo,
)


# Canonical names that MUST appear in canonical_columns / dataframe
EXPECTED_CANONICAL = set(CANONICAL_COLUMNS.keys())

# Physical names that MUST NOT leak into dataframe columns or canonical_columns
PHYSICAL_COLUMN_NAMES = ["COL_1", "STORE_NUM", "UPC_CODE", "ITEM_NAME", "PRICE_AMT", "UNITS"]

# Retailer-specific terms that must NOT appear in CanonicalMetadata
RETAILER_LEAKAGE_PATTERNS = [
    "delimiter", "pipe", "comma", "fixed_width", "multiline",
    "record_type", "header_prefix", "trailer_prefix", "layout",
    "start_line", "encoding_type", "character_distribution",
]


def _make_discovery_result_with_physical_columns() -> DiscoveryResult:
    """Build a DiscoveryResult whose physical columns are obviously retailer-specific."""
    return DiscoveryResult(
        file_path="/data/retailer_abc/SALES_2024.csv",
        file_type=FileType.DELIMITED,
        delimiter=",",
        delimiter_confidence=0.95,
        encoding="utf-8",
        has_header=True,
        header_confidence=0.99,
        columns=PHYSICAL_COLUMN_NAMES,

        candidate_store=[
            CandidateMapping(physical_column="STORE_NUM", confidence=0.92),
        ],
        candidate_upc=[
            CandidateMapping(physical_column="UPC_CODE", confidence=0.88),
        ],
        candidate_description=[
            CandidateMapping(physical_column="ITEM_NAME", confidence=0.85),
        ],
        candidate_units=[
            CandidateMapping(physical_column="UNITS", confidence=0.90),
        ],
        candidate_price=[
            CandidateMapping(physical_column="PRICE_AMT", confidence=0.87),
        ],
        candidate_store_type=[
            CandidateMapping(physical_column="COL_1", confidence=0.40),
        ],

        statistics=DetectionStatistics(
            estimated_rows=1500,
            header_confidence=0.99,
            schema_confidence=0.85,
        ),
        confidence=0.87,
        warnings=["Low confidence on COL_1"],
    )


def _make_dataframe_with_physical_columns() -> pl.DataFrame:
    """Create a DataFrame whose columns are the physical (retailer) names."""
    return pl.DataFrame({
        "STORE_NUM": [101, 102, 103],
        "UPC_CODE": ["123456789", "987654321", "111222333"],
        "ITEM_NAME": ["Widget", "Gadget", "Doohickey"],
        "PRICE_AMT": [9.99, 14.50, 3.25],
        "UNITS": [5, 12, 8],
        "COL_1": ["A", "B", "A"],
    })


class TestCanonicalNoPhysicalLeakage:
    """Verify the Canonical layer fully isolates physical schemas."""

    def test_canonical_columns_are_purely_canonical(self):
        """canonical_columns list must contain ONLY names from CANONICAL_COLUMNS."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        for col in dataset.canonical_columns:
            assert col in EXPECTED_CANONICAL, (
                f"Physical column '{col}' leaked into canonical_columns. "
                f"Expected one of: {sorted(EXPECTED_CANONICAL)}"
            )

    def test_dataframe_columns_are_canonical_when_data_provided(self):
        """DataFrame column names must be canonical, not physical.

        This is the critical isolation boundary: downstream consumers
        read dataset.dataframe and should never see physical names.
        """
        result = _make_discovery_result_with_physical_columns()
        data = _make_dataframe_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result, data=data)

        assert dataset.dataframe is not None
        df_columns = set(dataset.dataframe.columns)

        physical_set = set(PHYSICAL_COLUMN_NAMES)
        leaked = df_columns & physical_set
        assert not leaked, (
            f"Physical column names leaked into DataFrame: {leaked}. "
            f"DataFrame columns should be canonical names."
        )

    def test_mapping_dict_keys_are_internal_only(self):
        """physical_to_canonical dict must NOT be the only way to find columns.

        Downstream layers should use canonical_columns or dataframe.columns,
        not the physical_to_canonical dict.
        """
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        # canonical_columns should not require consulting physical_to_canonical
        for col in dataset.canonical_columns:
            assert col in EXPECTED_CANONICAL, (
                f"canonical_columns '{col}' is not a standard canonical name"
            )

    def test_metadata_has_no_retailer_specific_info(self):
        """CanonicalMetadata must NOT contain delimiter, record type, or layout details."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        meta = dataset.metadata
        assert meta is not None

        # Metadata should not store delimiter
        assert not hasattr(meta, "delimiter"), (
            "CanonicalMetadata must not have a 'delimiter' field"
        )

        # Check transformation log for physical schema leakage
        for entry in meta.transformation_log:
            for pattern in RETAILER_LEAKAGE_PATTERNS:
                assert pattern not in entry.lower(), (
                    f"Retailer-specific pattern '{pattern}' found in "
                    f"transformation_log: '{entry}'"
                )

    def test_metadata_source_file_type_is_abstract(self):
        """source_file_type must be a FileType value, not retailer-specific."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        meta = dataset.metadata
        valid_types = {ft.value for ft in FileType}
        assert meta.source_file_type in valid_types, (
            f"source_file_type '{meta.source_file_type}' is not a standard "
            f"FileType value: {valid_types}"
        )

    def test_no_physical_columns_in_dataframe_columns(self):
        """DataFrame columns must not contain any physical column name patterns."""
        result = _make_discovery_result_with_physical_columns()
        data = _make_dataframe_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result, data=data)

        if dataset.dataframe is not None:
            for col in dataset.dataframe.columns:
                assert col in EXPECTED_CANONICAL, (
                    f"Non-canonical column '{col}' found in DataFrame. "
                    f"Only canonical names allowed: {sorted(EXPECTED_CANONICAL)}"
                )

    def test_unmapped_columns_excluded_from_canonical(self):
        """Physical columns that have no canonical mapping must not appear in canonical_columns."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        # COL_1 maps to store_type → "store", UNITS → "quantity", etc.
        # Any physical column without a mapping should NOT appear in canonical_columns
        for col in dataset.canonical_columns:
            assert col in EXPECTED_CANONICAL, (
                f"Unmapped physical column '{col}' leaked into canonical_columns"
            )

    def test_quantity_column_is_canonical(self):
        """quantity_column in metadata must be a canonical name, not physical."""
        result = _make_discovery_result_with_physical_columns()
        data = _make_dataframe_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result, data=data)

        meta = dataset.metadata
        if meta.quantity_column is not None:
            assert meta.quantity_column in EXPECTED_CANONICAL, (
                f"quantity_column '{meta.quantity_column}' is a physical name, "
                f"not a canonical name. Expected one of: {sorted(EXPECTED_CANONICAL)}"
            )

    def test_downstream_contract_boundary(self):
        """Verify the full pipeline contract: after Canonical, only canonical names survive.

        Simulates what a downstream consumer would see.
        """
        result = _make_discovery_result_with_physical_columns()
        data = _make_dataframe_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result, data=data)

        # --- What downstream layers should see ---
        downstream_columns = set(dataset.canonical_columns)
        if dataset.dataframe is not None:
            downstream_columns |= set(dataset.dataframe.columns)

        # --- Physical names that must NOT appear ---
        forbidden = set(PHYSICAL_COLUMN_NAMES)
        leaked = downstream_columns & forbidden
        assert not leaked, (
            f"Physical schema leakage detected at downstream boundary: {leaked}. "
            f"Downstream consumers should only see canonical names."
        )

    def test_canonical_columns_subset_of_standard(self):
        """canonical_columns must be a subset of CANONICAL_COLUMNS."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        assert set(dataset.canonical_columns).issubset(set(CANONICAL_COLUMNS)), (
            f"canonical_columns {dataset.canonical_columns} contains non-standard names. "
            f"Standard: {sorted(CANONICAL_COLUMNS.keys())}"
        )

    def test_column_mappings_have_canonical_names(self):
        """Every ColumnMapping.canonical_name must be a standard canonical name."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        for mapping in dataset.column_mappings:
            assert mapping.canonical_name in EXPECTED_CANONICAL, (
                f"ColumnMapping has non-canonical canonical_name: '{mapping.canonical_name}'"
            )

    def test_no_retailer_info_in_warnings(self):
        """Warnings must not expose internal physical schema details."""
        result = _make_discovery_result_with_physical_columns()
        engine = CanonicalEngine()
        dataset = engine.transform(result)

        # Warnings can mention unmapped columns but not layout/delimiter details
        for warning in dataset.warnings:
            if isinstance(warning, str):
                for pattern in ["fixed_width", "multiline", "record_type", "layout"]:
                    assert pattern not in warning.lower(), (
                        f"Retailer-specific pattern '{pattern}' in warning: '{warning}'"
                    )
