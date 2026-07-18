You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 7 — Validation Layer.

Sprint 7 may begin ONLY after the complete regression gate has passed.

The following layers are FROZEN:

✓ Connection
✓ Detection
✓ Canonical
✓ Requirement
✓ Operation
✓ Processing
✓ Test Infrastructure

DO NOT modify frozen layers except for confirmed bug fixes.

==========================================================
OBJECTIVE
==========================================================

The Validation Layer is the business rule engine.

It evaluates the correctness of computed business results.

It NEVER performs computations.

It NEVER aggregates.

It NEVER calculates.

It NEVER generates reports.

It NEVER reparses data.

It NEVER accesses retailer schemas.

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

Processing
↓

Validation ← CURRENT SPRINT

↓

Output

↓

Flush

==========================================================
INPUT
==========================================================

Consumes ONLY:

ProcessingResult

AggregationResult

CalculationResult

ProcessingStatistics

Validation configuration

Business validation rules

==========================================================
OUTPUT
==========================================================

ValidationResult

ValidationSummary

ValidationStatistics

ValidationReportData

==========================================================
PRIMARY RESPONSIBILITIES
==========================================================

1. Store-Level Validation

Compare:

Expected Store Totals

Actual Store Totals

Validate:

Record Counts

Sales

Quantity

Weight

Variance

Tolerance

==========================================================
2. Item-Level Validation
==========================================================

Validate:

UPC totals

Sales

Quantity

Price

Weight

Category consistency

Missing items

Unexpected items

==========================================================
3. Aggregate Validation
==========================================================

Validate aggregate outputs.

Examples:

Store totals

Category totals

Brand totals

Department totals

Custom group totals

==========================================================
4. Business Rule Engine
==========================================================

Support configurable business rules.

Examples:

Difference Threshold

Percentage Threshold

Missing Records

Duplicate Records

Unexpected Categories

Unexpected Stores

Quantity mismatches

Sales mismatches

Null constraints

Business rule violations

Rules must be configurable.

==========================================================
5. Validation Severity
==========================================================

Support:

INFO

WARNING

ERROR

CRITICAL

Every validation result should include severity.

==========================================================
6. Validation Statistics
==========================================================

Generate:

Passed Rules

Failed Rules

Warning Count

Error Count

Critical Count

Validation Coverage

Execution Time

==========================================================
7. Validation Metadata
==========================================================

Produce metadata including:

Rules evaluated

Rules passed

Rules failed

Tolerance used

Thresholds applied

Execution duration

Warnings

Errors

==========================================================
8. Rule Extensibility
==========================================================

New validation rules should be pluggable.

Avoid modifying existing engine code.

Follow Strategy Pattern.

==========================================================
NON-NEGOTIABLE RULES
==========================================================

Validation performs NO aggregation.

Validation performs NO calculations.

Validation performs NO statistics generation.

Validation performs NO workflow planning.

Validation performs NO report generation.

Validation performs NO retailer parsing.

Validation NEVER modifies ProcessingResult.

Validation only evaluates.

==========================================================
SUGGESTED MODULES
==========================================================

engine.py

rules.py

validators.py

severity.py

statistics.py

metadata.py

configuration.py

contracts.py

exceptions.py

__init__.py

==========================================================
DESIGN PRINCIPLES
==========================================================

Single Responsibility

Strategy Pattern

Rule Engine Pattern

Open/Closed Principle

Dependency Injection

Composable Validators

No circular dependencies

==========================================================
VALIDATION RULES
==========================================================

Support rules such as:

Store Totals Match

UPC Totals Match

Quantity Match

Weight Match

Sales Match

Tolerance Check

Difference %

Duplicate Detection

Missing Store

Missing UPC

Unexpected Store

Unexpected UPC

Unexpected Category

Unexpected Brand

Null Required Fields

Custom Business Rules

==========================================================
TESTING
==========================================================

Create comprehensive tests covering:

Store validation

UPC validation

Business rule engine

Severity handling

Tolerance handling

Rule configuration

Metadata

Statistics

Edge cases

Large datasets

Custom rules

Integration with Processing

==========================================================
REGRESSION VALIDATION (MANDATORY)
==========================================================

Run the complete platform quality pipeline.

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

Streaming Tests

↓

Large Dataset Tests

↓

End-to-End Tests

↓

Coverage Review

If ANY regression is found:

1. Create a failing regression test.

2. Verify failure.

3. Fix implementation.

4. Re-run the complete quality pipeline.

Repeat until every suite passes.

Every bug fixed during Sprint 7 must receive a permanent regression test.

==========================================================
ARCHITECTURE REVIEW
==========================================================

Verify:

✓ Validation never aggregates.

✓ Validation never calculates.

✓ Validation never generates reports.

✓ Validation consumes ONLY Processing outputs.

✓ Validation never modifies ProcessingResult.

✓ No frozen layer modifications.

✓ No business logic duplication.

==========================================================
EXIT CRITERIA
==========================================================

✓ Validation engine complete

✓ Business rule engine complete

✓ Store validation complete

✓ Item validation complete

✓ Aggregate validation complete

✓ Severity framework complete

✓ Validation metadata complete

✓ Validation statistics complete

✓ Unit tests passing

✓ Integration tests passing

✓ Regression suite passing

✓ Architecture tests passing

✓ Contract tests passing

✓ Performance tests passing

✓ End-to-End tests passing

✓ Architecture review passed

==========================================================
FINAL DELIVERABLES
==========================================================

Produce a Sprint 7 Completion Report including:

1. Validation architecture

2. Business rule engine

3. Store validation

4. Item validation

5. Aggregate validation

6. Rule framework

7. Severity model

8. Validation metadata

9. Validation statistics

10. Test summary

11. Regression summary

12. Architecture audit

13. Remaining risks

If all quality gates pass:

1. Commit

2. Push

3. Tag:

v2-sprint7-complete

Freeze the Validation Layer.

Do not proceed to Sprint 8 until the full regression suite passes again.
