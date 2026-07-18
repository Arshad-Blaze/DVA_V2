# DVA Platform v2
# Sprint 3 — Canonical Layer Plan

**Status:** PLANNING (Do not begin implementation until approved)
**Depends on:** Sprint 2.5 (Detection Layer) — FROZEN

---

## Overview

The Canonical Layer converts physical data (as detected by Detection) into a standardized business format. It is the bridge between raw file structure and business logic.

Detection says: "Here is what the file looks like."
Canonical says: "Here is what the data means."

---

## Canonical Layer Responsibilities

1. **Schema Mapping** — Map physical column names to standard business names
2. **Column Selection** — Choose which columns to include in output
3. **Quantity Resolution** — Resolve quantity from weighted_qty, units, or custom
4. **Type Coercion** — Convert string values to appropriate types (numeric, date, etc.)
5. **Canonical DataFrame Generation** — Produce a standardized Polars DataFrame
6. **Canonical Preview** — Generate a preview of the mapped data

---

## Contract

**Input:** `DiscoveryResult` (from Detection Layer)
**Output:** `CanonicalDataset` (consumed by Requirement/Processing layers)

```python
@dataclass
class CanonicalDataset:
    """Standardized dataset ready for processing."""
    file_path: str
    physical_to_canonical: Dict[str, str]  # physical_col -> canonical_name
    canonical_columns: List[str]           # ordered canonical column names
    dataframe: Optional[pl.DataFrame]      # the actual data (streamed or sampled)
    metadata: CanonicalMetadata
    warnings: List[str]
    recommendations: List[str]

@dataclass
class CanonicalMetadata:
    """Metadata about the canonical transformation."""
    total_rows: int
    mapped_columns: int
    unmapped_columns: int
    quantity_column: Optional[str]
    quantity_type: str  # "weighted_qty", "units", "none"
    confidence: float
```

---

## Standard Canonical Columns

| Canonical Name | Description | Type |
|----------------|-------------|------|
| `store` | Store identifier | str |
| `upc` | Universal Product Code | str |
| `description` | Product description | str |
| `quantity` | Resolved quantity (weighted or units) | float |
| `weight` | Weight value (if available) | float |
| `price` | Unit price | float |
| `category` | Product category | str |
| `brand` | Product brand | str |
| `department` | Department identifier | str |
| `date` | Transaction date | date |
| `uom` | Unit of measure | str |

---

## Mapping Engine

### Strategy Pattern

The mapping engine supports multiple strategies:

1. **Candidate-Based Mapping** — Uses Detection's candidate columns directly
2. **Rule-Based Mapping** — Applies retailer-specific rules (e.g., "if column contains 'WTD', map to weight")
3. **User-Defined Mapping** — Accepts manual overrides from UI/config

### Mapping Priority

```
User-Defined > Rule-Based > Candidate-Based > Default
```

### Mapping Process

1. Receive `DiscoveryResult` with candidate columns
2. For each canonical column, find best match:
   - Check user overrides first
   - Check retailer-specific rules
   - Use candidate mapping with highest confidence
   - Apply default if no match found
3. Generate `physical_to_canonical` mapping dict
4. Validate mapping completeness
5. Return mapping with confidence scores

---

## Quantity Resolution

The Canonical Layer resolves quantity based on Detection's recommendation:

```python
def resolve_quantity(result: DiscoveryResult) -> Tuple[Optional[str], str]:
    """Resolve which column represents quantity.

    Returns:
        (column_name, quantity_type)
    """
    if result.quantity_recommendation:
        rec = result.quantity_recommendation
        if rec.recommendation_type != "none":
            return rec.recommended_column, rec.recommendation_type

    # Fallback: check candidates directly
    if result.candidate_weighted_qty:
        return result.candidate_weighted_qty[0].physical_column, "weighted_qty"
    if result.candidate_units:
        return result.candidate_units[0].physical_column, "units"

    return None, "none"
```

---

## Type Coercion

| Canonical Type | Source Detection | Coercion |
|----------------|------------------|----------|
| `str` | All columns | Default — no transformation |
| `float` | price, weight, quantity | `float(str_value)` with NaN on failure |
| `int` | store, upc | `int(str_value)` with fallback to str |
| `date` | date column | Parse with multiple formats |

---

## Modules

| Module | Responsibility |
|--------|---------------|
| `canonical_engine.py` | Main orchestrator |
| `mapping.py` | Column mapping logic |
| `quantity.py` | Quantity resolution |
| `coercion.py` | Type coercion |
| `preview.py` | Canonical preview generation |
| `context.py` | Internal CanonicalContext |

---

## Inputs (from Detection)

| Field | Usage |
|-------|-------|
| `DiscoveryResult.columns` | Physical column names |
| `DiscoveryResult.candidate_*` (19 roles) | Mapping candidates |
| `DiscoveryResult.quantity_recommendation` | Quantity strategy |
| `DiscoveryResult.delimiter` | For parsing |
| `DiscoveryResult.file_type` | For parsing strategy |
| `DiscoveryResult.record_types` | For row classification |
| `DiscoveryResult.has_header` | For header handling |
| `DiscoveryResult.raw_preview` | For preview generation |

---

## Outputs (to Requirement/Processing)

| Output | Description |
|--------|-------------|
| `CanonicalDataset.physical_to_canonical` | Column mapping dict |
| `CanonicalDataset.canonical_columns` | Ordered list of canonical columns |
| `CanonicalDataset.dataframe` | Standardized DataFrame |
| `CanonicalDataset.metadata` | Transformation metadata |
| `CanonicalDataset.warnings` | Issues encountered |
| `CanonicalDataset.recommendations` | Suggestions for user |

---

## Extension Points

1. **Custom Mapping Rules** — Retailer-specific mapping configurations
2. **Custom Coercion** — Retailer-specific type conversions
3. **Custom Quantity Logic** — Retailer-specific quantity resolution
4. **Post-Mapping Hooks** — Validation or enrichment after mapping

---

## Testing Strategy

### Unit Tests
- Mapping engine with mock DiscoveryResult
- Quantity resolution for all scenarios
- Type coercion with edge cases
- Preview generation

### Integration Tests
- Full Detection → Canonical pipeline
- End-to-end with sample datasets
- Mapping accuracy for known retailers

### Regression Tests
- Ensure Detection output format hasn't changed
- Verify Canonical output matches expected schema

### Sample Datasets
- Simple CSV (3 columns)
- Multiline pipe-delimited
- Fixed-width with layout
- Excel workbook
- Mixed record types (H/D/T)

---

## Sequence Diagram

```
User → DetectionEngine → DiscoveryResult → CanonicalEngine → CanonicalDataset
                  ↓                              ↓
         [Frozen Layer]              [New Layer - Sprint 3]
```

---

## Dependency Diagram

```
IDataSource (Sprint 1) → DetectionEngine (Sprint 2.5) → CanonicalEngine (Sprint 3)
                                                            ↓
                                                    CanonicalDataset → Requirement (Sprint 4)
```

---

## Risks

| Risk | Mitigation |
|------|------------|
| Detection output changes | Detection is FROZEN — no changes allowed |
| Mapping accuracy | Candidate detection provides confidence scores |
| Quantity resolution | Multiple fallback strategies |
| Type coercion failures | Graceful NaN/fallback handling |

---

## Success Criteria

- [ ] CanonicalEngine produces CanonicalDataset from any DiscoveryResult
- [ ] Physical-to-canonical mapping covers all 19 candidate roles
- [ ] Quantity resolution handles weighted_qty, units, and none
- [ ] Type coercion handles string, float, int, date
- [ ] Preview generation produces readable output
- [ ] All unit tests pass
- [ ] Integration with Detection works end-to-end
- [ ] Layer boundaries maintained (no Detection re-implementation)

---

## Notes

- Do NOT begin implementation until this plan is reviewed and approved
- Detection Layer is FROZEN — do not modify
- Follow Architecture Bible: one responsibility, one contract, no bypasses
- Use Polars for all DataFrame operations
- Streaming-first: read data in chunks, don't load full files
