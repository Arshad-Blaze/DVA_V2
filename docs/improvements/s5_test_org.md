You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 5.5 — Test Infrastructure & Quality Framework.

NO NEW BUSINESS FEATURES.

NO ARCHITECTURE CHANGES.

The purpose of this sprint is to organize, standardize and future-proof the entire automated test suite before beginning the Processing Layer.

The following layers are frozen:

✓ Connection
✓ Detection
✓ Canonical
✓ Requirement
✓ Operation

They must remain unchanged except for critical bug fixes discovered during testing.

==========================================================
OBJECTIVE
==========================================================

Transform the current collection of tests into a structured enterprise-grade quality framework.

The goal is that every future sprint automatically validates:

Correctness

Architecture

Contracts

Regression

Performance

End-to-End behaviour

==========================================================
PHASE 1 — TEST REORGANIZATION
==========================================================

Organize the entire test suite into logical categories.

Recommended structure:

tests/

    unit/

        connection/

        detection/

        canonical/

        requirement/

        operation/

        processing/

        validation/

        output/

    integration/

        connection_detection/

        detection_canonical/

        canonical_requirement/

        requirement_operation/

        operation_processing/

        processing_validation/

        validation_output/

    regression/

        bugs/

        contracts/

        architecture/

        performance/

    e2e/

        retailer_scenarios/

        onboarding/

        migration/

        format_change/

        reporting/

        validation/

==========================================================
PHASE 2 — TEST TAGGING
==========================================================

Every test should belong to one or more categories.

Examples

@pytest.mark.unit

@pytest.mark.integration

@pytest.mark.regression

@pytest.mark.architecture

@pytest.mark.performance

@pytest.mark.e2e

@pytest.mark.streaming

@pytest.mark.large_dataset

Avoid ambiguous classifications.

==========================================================
PHASE 3 — REGRESSION FRAMEWORK
==========================================================

Create a permanent regression suite.

Every bug ever fixed must have

one

and only one

dedicated regression test.

Regression tests should never be removed.

Organize by bug rather than module.

==========================================================
PHASE 4 — CONTRACT TESTS
==========================================================

Create dedicated contract tests.

Verify stability of:

IDataSource

DiscoveryResult

CanonicalDataset

CanonicalMetadata

OperationContext

ExecutionPlan

ExecutionResult

ExecutionMetadata

OperationLog

ExecutionState

Public APIs must remain backward compatible.

==========================================================
PHASE 5 — ARCHITECTURE TESTS
==========================================================

Automatically verify:

No circular dependencies

No frozen layer modifications

No layer bypasses

No UI imports

No retailer-specific logic outside Canonical

No Processing imports inside Requirement

No business logic inside Operation

Layer boundaries remain intact.

==========================================================
PHASE 6 — PERFORMANCE TESTS
==========================================================

Create baseline performance tests.

Measure:

Streaming behaviour

Chunk processing

Memory usage

Large dataset execution

Transformation cost

Execution overhead

These become reference baselines for future sprints.

==========================================================
PHASE 7 — END-TO-END TESTS
==========================================================

Create representative end-to-end scenarios.

Examples

Delimited retailer

Fixed Width retailer

Multiline retailer

Mixed Record Types

Weight-only datasets

Units-only datasets

Mixed datasets

Migration

Validation

Report generation

These tests should execute the entire pipeline using frozen layers.

==========================================================
PHASE 8 — TEST UTILITIES
==========================================================

Create reusable helpers.

Examples

Sample dataset builders

Canonical dataset factories

Execution plan builders

Mock data sources

Mock handlers

Random dataset generators

Large dataset generators

Avoid duplicated setup code.

==========================================================
PHASE 9 — COVERAGE REVIEW
==========================================================

Review current coverage.

Identify:

Duplicate tests

Weak coverage

Untested contracts

Missing edge cases

Remove redundant tests only when coverage is preserved.

==========================================================
PHASE 10 — TEST DOCUMENTATION
==========================================================

Document:

Test hierarchy

Naming conventions

How to add tests

Regression policy

Bug reproduction policy

Performance benchmarks

Architecture validation

Developer workflow

==========================================================
BUG POLICY
==========================================================

Every future bug must follow this workflow.

Bug discovered

↓

Write failing regression test

↓

Verify failure

↓

Fix implementation

↓

Verify regression passes

↓

Run full regression suite

↓

Commit bug fix and regression test together

No bug may be fixed without a permanent regression test.

==========================================================
REGRESSION VALIDATION
==========================================================

Run the complete quality pipeline.

Unit Tests

↓

Integration Tests

↓

Regression Tests

↓

Architecture Tests

↓

Contract Tests

↓

Performance Tests

↓

End-to-End Tests

↓

Coverage Review

Fix any issues discovered.

Repeat until all tests pass.

==========================================================
DELIVERABLES
==========================================================

Produce a Test Infrastructure Report including:

1. Test hierarchy

2. Test categories

3. Coverage summary

4. Regression framework

5. Architecture validation framework

6. Contract validation framework

7. Performance framework

8. End-to-end framework

9. Developer testing guidelines

10. Remaining quality risks

==========================================================
EXIT CRITERIA
==========================================================

✓ Test suite reorganized

✓ Test categories established

✓ Regression framework complete

✓ Contract tests complete

✓ Architecture tests complete

✓ Performance tests complete

✓ End-to-end tests complete

✓ Documentation complete

✓ All tests passing

✓ No frozen layer regressions

Finally:

Run the entire quality pipeline.

Fix any regressions.

Commit.

Push.

Tag:

v2-test-framework-complete
