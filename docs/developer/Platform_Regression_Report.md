# Platform Regression Report — Sprint 6.5

**Date:** 2026-07-18
**Platform Version:** v2 (Sprint 6 complete)
**Quality Gate:** ✅ PASSED

---

## Frozen Layers

| Layer | Status |
|---|---|
| Connection | ✅ Frozen |
| Detection | ✅ Frozen |
| Canonical | ✅ Frozen |
| Requirement | ✅ Frozen |
| Operation | ✅ Frozen |
| Processing | ✅ Frozen |
| Test Infrastructure | ✅ Frozen |

## Test Summary

| Category | Count |
|---|---|
| Unit Tests | 470 |
| Integration Tests | 57 |
| Regression Tests | 145 |
| E2E Tests | 9 |
| **Total** | **681** |

### By Marker

| Marker | Count |
|---|---|
| `@pytest.mark.unit` | 470 |
| `@pytest.mark.integration` | 57 |
| `@pytest.mark.regression` | 145 |
| `@pytest.mark.architecture` | 27 |
| `@pytest.mark.contract` | 86 |
| `@pytest.mark.performance` | 11 |
| `@pytest.mark.e2e` | 9 |
| Streaming (by file) | 20 |

## Architecture Audit

| Check | Result |
|---|---|
| Frozen layers untouched | ✅ PASS |
| No circular dependencies | ✅ PASS |
| No layer bypasses | ✅ PASS |
| No business logic in operations/ | ✅ PASS |
| No retailer-specific logic | ✅ PASS |
| Processing performs computations ONLY | ✅ PASS |

## Contract Regression

| Contract | Status |
|---|---|
| IDataSource | ✅ Stable |
| DiscoveryResult | ✅ Stable |
| CanonicalDataset | ✅ Stable |
| CanonicalMetadata | ✅ Stable |
| OperationContext | ✅ Stable |
| ExecutionResult | ✅ Stable |
| ExecutionMetadata | ✅ Stable |
| OperationLog | ✅ Stable |
| ExecutionState | ✅ Stable |
| ExecutionStepResult | ✅ Stable |
| ProcessingResult | ✅ Stable |
| AggregationResult | ✅ Stable |
| AggregationConfig | ✅ Stable |
| AggregationStrategy | ✅ Stable |
| CalculationResult | ✅ Stable |
| CalculationConfig | ✅ Stable |
| ProcessingStatistics | ✅ Stable |
| ProcessingConfig | ✅ Stable |

All 18 contracts verified. All exported from `core/__init__.py`.

## Performance Regression

| Test | Result |
|---|---|
| Streaming 100k rows | ✅ <2s |
| Chunk processing (100/1k/10k) | ✅ All pass |
| Memory estimation | ✅ Positive for all inputs |
| Canonical transform 10k rows | ✅ <1s |
| UOM normalization 10k rows | ✅ <0.5s |

## E2E Validation

| Scenario | Result |
|---|---|
| Delimited retailer | ✅ Pass |
| Fixed-width retailer | ✅ Pass |
| Multiline retailer | ✅ Pass |
| AGGREGATE_AND_CALCULATE pipeline | ✅ Pass |
| AGGREGATE_ONLY pipeline | ✅ Pass |
| RAW_REVIEW pipeline | ✅ Pass |
| Pipeline with failures | ✅ Pass |
| Context immutability | ✅ Pass |
| Operation → Processing integration | ✅ Pass |

## Bugs Discovered

None during this regression gate.

## Final Quality Status

| Gate | Status |
|---|---|
| All tests pass | ✅ |
| Regression suite passes | ✅ |
| Architecture tests pass | ✅ |
| Contract tests pass | ✅ |
| Performance tests pass | ✅ |
| Streaming tests pass | ✅ |
| End-to-End tests pass | ✅ |
| No architecture violations | ✅ |
| No contract regressions | ✅ |
| No unresolved bugs | ✅ |

**All quality gates passed. Sprint 7 may begin.**
