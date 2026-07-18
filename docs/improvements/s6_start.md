You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 6 — Processing Layer.

The following layers are FROZEN and MUST NOT be modified except for critical bug fixes discovered during testing.

✓ Connection
✓ Detection
✓ Canonical
✓ Requirement
✓ Operation
✓ Test Infrastructure & Quality Framework

Follow the Architecture Bible exactly.

==========================================================
OBJECTIVE
==========================================================

The Processing Layer is the computation engine.

Its responsibility is to execute business computations requested by the Operation Layer.

It MUST NOT:

- decide workflows
- make business decisions
- validate business correctness
- generate reports
- know retailer formats
- know physical schemas

It performs computations ONLY.

==========================================================
PIPELINE
==========================================================

Connection
↓

Detection
↓

Canonical
↓

Requirement
↓

Operation
↓

Processing ← CURRENT SPRINT

↓

Validation

↓

Output

↓

Flush

==========================================================
INPUT
==========================================================

Consumes ONLY:

ExecutionResult / ExecutionPlan

CanonicalDataset

CanonicalMetadata

Processing configuration

==========================================================
OUTPUT
==========================================================

ProcessingResult

AggregationResult

CalculationResult

ProcessingStatistics

==========================================================
PRIMARY RESPONSIBILITIES
==========================================================

1. Aggregation Engine

Implement reusable aggregation engine.

Support:

Store Level

UPC Level

Category Level

Department Level

Brand Level

Custom Grouping

User-defined grouping

No retailer-specific logic.

==========================================================
2. Calculation Engine
==========================================================

Implement calculations.

Support:

Record Count

Units

Weight

Sales

Average

Minimum

Maximum

Difference

Difference %

Ratios

Totals

Custom expressions

All calculations must operate on canonical fields.

==========================================================
3. Statistics Engine
==========================================================

Generate processing statistics.

Examples:

Row counts

Unique stores

Unique UPCs

Categories

Brands

Departments

Duplicate counts

Null counts

Distribution summaries

==========================================================
4. Streaming Processing
==========================================================

Support chunk-based processing.

Avoid loading entire datasets into memory.

Support multi-GB retailer files.

Maintain streaming architecture established by Canonical.

==========================================================
5. Processing Pipeline
==========================================================

Implement a modular computation pipeline.

Example:

CanonicalDataset

↓

Aggregate

↓

Calculate

↓

Statistics

↓

ProcessingResult

Each stage should be independently testable.

==========================================================
6. Processing Metadata
==========================================================

Produce metadata including:

Aggregation strategy

Calculation strategy

Grouping columns

Calculation columns

Rows processed

Chunks processed

Execution duration

Performance metrics

Warnings

==========================================================
7. Processing Configuration
==========================================================

Support configurable processing.

Examples:

Grouping columns

Aggregation columns

Calculation list

Chunk size

Streaming options

Parallel execution flags (design only; no premature optimization)

==========================================================
8. Extensibility
==========================================================

Design for future processing modules.

New calculations should be pluggable.

New aggregation strategies should require minimal changes.

Follow Open/Closed Principle.

==========================================================
NON-NEGOTIABLE RULES
==========================================================

Processing performs NO business validation.

Processing performs NO workflow selection.

Processing performs NO report generation.

Processing performs NO UI work.

Processing performs NO retailer-specific logic.

Processing never accesses physical schemas.

Processing consumes ONLY canonical business data.

==========================================================
SUGGESTED MODULES
==========================================================

engine.py

aggregator.py

calculator.py

statistics.py

streaming.py

configuration.py

contracts.py

pipeline.py

metadata.py

exceptions.py

__init__.py

==========================================================
DESIGN PRINCIPLES
==========================================================

Single Responsibility

Pipeline Pattern

Strategy Pattern

Dependency Injection

Streaming First

Composable Computations

Small focused modules

No circular dependencies

==========================================================
TESTING
==========================================================

Create comprehensive tests for:

Aggregation

Calculations

Statistics

Streaming

Large datasets

Chunk processing

Grouping

Custom calculations

Edge cases

Memory usage

Metadata generation

Pipeline execution

Integration with Operation

==========================================================
REGRESSION VALIDATION (MANDATORY)
==========================================================

Run the complete project quality pipeline.

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

If ANY regression is detected:

1. Write a regression test reproducing it.
2. Verify the test fails.
3. Fix the implementation.
4. Re-run the full quality pipeline.
5. Repeat until all tests pass.

Every bug fixed during Sprint 6 MUST have a permanent regression test.

==========================================================
ARCHITECTURE REVIEW
==========================================================

Verify:

✓ Processing performs computations ONLY

✓ No validation logic

✓ No workflow decisions

✓ No retailer-specific logic

✓ No physical schema leakage

✓ Uses only CanonicalDataset

✓ No frozen layer modifications

==========================================================
EXIT CRITERIA
==========================================================

✓ Aggregation engine complete

✓ Calculation engine complete

✓ Statistics engine complete

✓ Streaming processing complete

✓ Processing metadata complete

✓ Processing configuration complete

✓ Unit tests passing

✓ Integration tests passing

✓ Regression suite passing

✓ Architecture tests passing

✓ Contract tests passing

✓ Performance tests passing

✓ End-to-end tests passing

✓ Architecture review passed

==========================================================
FINAL DELIVERABLES
==========================================================

Produce a Sprint 6 Completion Report containing:

1. Processing architecture

2. Aggregation engine

3. Calculation engine

4. Statistics engine

5. Streaming implementation

6. Configuration model

7. Processing metadata

8. Performance characteristics

9. Test summary

10. Regression summary

11. Architecture audit

12. Remaining risks

If all exit criteria are satisfied:

1. Commit
2. Push
3. Tag:

v2-sprint6-complete

Do NOT freeze the Processing Layer until the completion report confirms that all quality gates and regression checks have passed.
