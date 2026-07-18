# DVA Platform v2
# Sprint 4 — Requirement Layer Plan

**Status:** IMPLEMENTING
**Depends on:** Sprint 3C (Canonical Layer) — FROZEN

---

## Overview

The Requirement Layer bridges Canonical data and Operation intent. It translates user intent (what they want to do) into a structured `OperationContext` that the Operation Layer consumes.

Detection says: "Here is what the file looks like."
Canonical says: "Here is what the data means."
Requirement says: "Here is what the user wants to do with it."

---

## Requirement Layer Responsibilities

1. **Mode Selection** — User selects processing mode (Aggregate Only / Aggregate + Calculate / Raw Review)
2. **Mode Validation** — Validate that canonical data supports the selected mode
3. **Option Configuration** — User configures processing options
4. **Context Building** — Build `OperationContext` with mode, options, session, and metadata
5. **Data Readiness Check** — Verify canonical data is ready for the selected operation

---

## Contract

**Input:** `CanonicalDataset` + `CanonicalMetadata` (from Canonical Layer)
**Output:** `OperationContext` (consumed by Operation Layer)

```python
class ProcessingMode(Enum):
    AGGREGATE_ONLY = "aggregate_only"
    AGGREGATE_AND_CALCULATE = "aggregate_and_calculate"
    RAW_REVIEW = "raw_review"

@dataclass
class OperationContext:
    mode: ProcessingMode
    options: Dict[str, Any]
    session_id: str
    metadata: Dict[str, Any]
```

---

## Module Design

### 1. `mode_selector.py` — Mode Selection

Handles user selection of processing mode.

- `select_mode(mode: ProcessingMode) -> ProcessingMode` — Select a processing mode
- `get_available_modes(dataset: CanonicalDataset) -> List[ProcessingMode]` — Get modes available for this dataset
- `suggest_mode(dataset: CanonicalDataset) -> ProcessingMode` — Auto-suggest best mode

Mode availability rules:
- `RAW_REVIEW`: Always available if dataset has data
- `AGGREGATE_ONLY`: Available if dataset has at least one groupable column (store, brand, category, department)
- `AGGREGATE_AND_CALCULATE`: Available if dataset has quantity column AND at least one groupable column

### 2. `validator.py` — Mode Validation

Validates that the selected mode is compatible with the canonical data.

- `validate_mode(mode, dataset) -> ValidationResult` — Validate mode against dataset
- `check_data_readiness(dataset) -> List[str]` — Check if data is ready for processing

Validation rules:
- Dataset must not be None or empty
- For AGGREGATE modes: must have groupable columns
- For AGGREGATE_AND_CALCULATE: must have quantity column
- Canonical columns must be present in DataFrame

### 3. `context_builder.py` — Context Building

Builds the OperationContext from mode + canonical data.

- `build_context(mode, dataset, options) -> OperationContext` — Build context
- `build_session_id() -> str` — Generate unique session ID
- `extract_metadata(dataset) -> Dict[str, Any]` — Extract relevant metadata

Context metadata includes:
- `file_path`: Source file path
- `total_rows`: Row count
- `canonical_columns`: Available columns
- `quantity_column`: Quantity column name
- `quantity_type`: Weight/Unit/None
- `has_data`: Whether DataFrame is present
- `row_count`: DataFrame row count

### 4. `engine.py` — Requirement Orchestrator

Main entry point for the Requirement Layer.

- `RequirementLayer.process(dataset, mode, options) -> OperationContext` — Full pipeline

Pipeline:
1. Validate mode availability
2. Validate mode against dataset
3. Build context
4. Return OperationContext

---

## Architecture Compliance

| Rule | Compliance |
|------|------------|
| ONE responsibility | YES — user intent translation |
| ONE contract | YES — `OperationContext` |
| Consumes ONLY previous layer's output | YES — `CanonicalDataset` only |
| No layer bypasses | YES — does not access Detection or Connection |
| No duplicate logic | YES — mode validation is unique to this layer |
| No retailer-specific logic | YES — operates on canonical data only |
| Streaming compatible | YES — works with chunk-level datasets |

---

## File Structure

```
dav_platform/requirements/
    __init__.py          # Exports RequirementLayer, OperationContext, ProcessingMode
    mode_selector.py     # Mode selection and availability
    validator.py         # Mode validation against dataset
    context_builder.py   # OperationContext construction
    engine.py            # RequirementLayer orchestrator
```

---

## Tests

```
tests/unit/
    test_requirement_mode_selector.py    # Mode selection tests
    test_requirement_validator.py        # Validation tests
    test_requirement_context_builder.py  # Context building tests
    test_requirement_engine.py           # Engine orchestrator tests
tests/integration/
    test_canonical_to_requirement.py     # Canonical → Requirement pipeline
```

---

## Implementation Order

1. `mode_selector.py` + tests
2. `validator.py` + tests
3. `context_builder.py` + tests
4. `engine.py` + tests
5. `__init__.py` exports
6. Integration tests
7. Wire up coercion.py (optional, from Sprint 3C note)
8. Full test suite verification
9. Completion report + commit + tag
