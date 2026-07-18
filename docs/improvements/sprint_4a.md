You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 4A — Requirement Foundation.

The Connection, Detection and Canonical layers are frozen.

DO NOT modify frozen layers except for critical bug fixes.

==========================================================
OBJECTIVE
==========================================================

Build the foundational Requirement Layer.

The Requirement Layer converts user processing intent into a structured OperationContext.

It does NOT execute business logic.

It does NOT aggregate.

It does NOT calculate.

It does NOT validate business rules.

It simply determines whether the requested operation is possible and builds a clean execution context.

==========================================================
INPUT
==========================================================

Consumes ONLY:

CanonicalDataset

CanonicalMetadata

User-selected mode

Optional user processing options

==========================================================
OUTPUT
==========================================================

OperationContext

This is the ONLY public contract.

==========================================================
IMPLEMENT
==========================================================

1. Processing Modes

Support:

RAW_REVIEW

AGGREGATE_ONLY

AGGREGATE_AND_CALCULATE

==========================================================

2. Mode Selection

Support:

User-selected mode

Automatic recommendation

Mode availability checking

Graceful fallback

==========================================================

3. Dataset Readiness Validation

Verify:

Dataset exists

Rows exist

Required grouping columns

Quantity column availability

Basic processing readiness

==========================================================

4. Context Builder

Build OperationContext containing:

Processing mode

Options

Session ID

Dataset summary

Canonical metadata

Validation status

==========================================================

5. Requirement Engine

Create a single orchestrator.

Responsibilities:

Receive CanonicalDataset

Validate

Select mode

Build OperationContext

Return OperationContext

==========================================================
ARCHITECTURE RULES
==========================================================

Requirement performs NO processing.

Requirement performs NO aggregation.

Requirement performs NO calculations.

Requirement performs NO retailer-specific logic.

Requirement never modifies CanonicalDataset.

==========================================================
TESTS
==========================================================

Create tests covering:

Mode selection

Mode recommendation

Validation

Context construction

Canonical → Requirement integration

==========================================================
EXIT CRITERIA
==========================================================

✓ Stable OperationContext

✓ Tests passing

✓ Architecture review passed

✓ No frozen layer modifications

Produce a completion report.

Commit and push.
