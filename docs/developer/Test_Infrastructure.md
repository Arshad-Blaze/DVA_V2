# DVA Platform V2 — Test Infrastructure & Quality Framework

## Test Hierarchy

```
tests/
├── conftest.py                          # Root fixtures and factories
├── unit/                                # Fast, isolated tests
│   ├── connection/                      # Connection Layer tests
│   ├── detection/                       # Detection Layer tests
│   ├── canonical/                       # Canonical Layer tests
│   ├── requirement/                     # Requirement Layer tests
│   ├── operation/                       # Operation Layer tests
│   ├── processing/                      # (future)
│   ├── validation/                      # (future)
│   └── output/                          # (future)
├── integration/                         # Multi-layer contract tests
│   ├── connection_detection/
│   ├── detection_canonical/
│   ├── canonical_requirement/
│   ├── requirement_operation/
│   ├── operation_processing/
│   ├── processing_validation/
│   └── validation_output/
├── regression/                          # Permanent regression guards
│   ├── bugs/                            # Bug-specific regression tests
│   ├── contracts/                       # Contract stability tests
│   ├── architecture/                    # Architecture integrity tests
│   └── performance/                     # Performance baseline tests
└── e2e/                                 # Full pipeline scenarios
    └── retailer_scenarios/
```

## Test Categories (Markers)

| Marker | Description | Example |
|--------|-------------|---------|
| `@pytest.mark.unit` | Fast, isolated, no I/O | `test_canonical_mapping.py` |
| `@pytest.mark.integration` | Multi-layer, contract verification | `test_canonical_to_requirement.py` |
| `@pytest.mark.regression` | Bug fixes, contract stability | `test_contract_stability.py` |
| `@pytest.mark.architecture` | Layer isolation, imports, SRP | `test_architecture_integrity.py` |
| `@pytest.mark.contract` | API stability, field access | `test_contract_stability.py` |
| `@pytest.mark.performance` | Memory, streaming, timing | `test_performance_baselines.py` |
| `@pytest.mark.e2e` | Full pipeline scenarios | `test_full_pipeline.py` |
| `@pytest.mark.streaming` | Streaming/chunked processing | Canonical streaming tests |
| `@pytest.mark.slow` | Tests taking >1s | Performance benchmarks |

## Running Tests

```bash
# All tests
python3 -m pytest tests/ -v

# By category
python3 -m pytest tests/ -m unit -v
python3 -m pytest tests/ -m integration -v
python3 -m pytest tests/ -m regression -v
python3 -m pytest tests/ -m architecture -v
python3 -m pytest tests/ -m contract -v
python3 -m pytest tests/ -m performance -v
python3 -m pytest tests/ -m e2e -v

# Exclude slow tests
python3 -m pytest tests/ -m "not slow" -v

# By layer
python3 -m pytest tests/unit/connection/ -v
python3 -m pytest tests/unit/canonical/ -v
```

## How to Add Tests

### Unit Test
1. Create `tests/unit/<layer>/test_<module>.py`
2. Import from `dav_platform.<layer>.<module>`
3. Add `@pytest.mark.unit` decorator
4. Use fixtures from `tests/conftest.py`

### Integration Test
1. Create `tests/integration/<layer_pair>/test_<flow>.py`
2. Import from both layers involved
3. Add `@pytest.mark.integration` decorator
4. Test the contract boundary between layers

### Regression Test
1. Create or add to `tests/regression/bugs/test_bug_<id>.py`
2. Add `@pytest.mark.regression` decorator
3. Include bug ID and description in docstring
4. Never remove regression tests

### Performance Test
1. Create in `tests/regression/performance/`
2. Add `@pytest.mark.performance` and `@pytest.mark.slow` decorators
3. Include timing assertions with reasonable thresholds
4. Document baseline numbers in docstring

## Bug Policy

Every bug must follow this workflow:

1. Bug discovered
2. Write failing regression test
3. Verify failure
4. Fix implementation
5. Verify regression passes
6. Run full regression suite
7. Commit bug fix and regression test together

**No bug may be fixed without a permanent regression test.**

## Architecture Validation

Automatically verified on every run:

- Frozen layers (Connection, Detection, Canonical, Requirement, Operation) never import from layers behind them
- No circular dependencies between layers
- No layer bypasses (operations doesn't import from detection/connection)
- No business logic in operations layer
- No UI framework imports in business layers
- No retailer-specific logic outside canonical layer
- Each layer has exactly one entry point
- No god modules (>500 lines, excluding contracts)

## Contract Validation

All public contracts verified for backward compatibility:

- `IDataSource` — 15 methods, ABC interface
- `DiscoveryResult` — 30+ fields, all dataclass fields
- `CanonicalDataset` — 8 fields + 4 properties
- `CanonicalMetadata` — 15 fields
- `OperationContext` — 13 fields
- `ExecutionResult` — 7 fields + 3 boolean properties
- `ExecutionMetadata` — 9 fields
- `OperationLog` — 7 fields
- `ExecutionState` — 6 enum values

## Performance Baselines

Reference baselines for future sprints:

- Streaming 100k rows: <2s
- Canonical transform 10k rows: <1s
- UOM normalization 10k rows: <0.5s
- Memory estimation: positive for all inputs

## Shared Fixtures

Available from `tests/conftest.py`:

| Fixture | Description |
|---------|-------------|
| `sample_delimited_data` | Pipe-delimited file content |
| `sample_fixed_width_data` | Fixed-width file content |
| `sample_multiline_data` | Multiline file content |
| `sample_dataframe` | 3-row polars DataFrame |
| `large_dataframe` | 100k-row polars DataFrame |
| `canonical_dataset_with_data` | CanonicalDataset with DataFrame |
| `canonical_dataset_no_data` | CanonicalDataset without DataFrame |
| `operation_context_basic` | Basic OperationContext |
| `mock_handler` | Factory for mock operation handlers |
| `tmp_csv_file` | Factory for temp CSV files |
