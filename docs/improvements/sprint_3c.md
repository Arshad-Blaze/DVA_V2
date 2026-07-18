You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 3C — Canonical Validation & Freeze.

Sprint 3A (Canonical Foundation) and Sprint 3B (Canonical Transformation Engine) are COMPLETE.

DO NOT redesign the Canonical Layer.

DO NOT introduce new architecture.

DO NOT perform unnecessary refactoring.

The purpose of Sprint 3C is to validate, optimize, harden and freeze the Canonical Layer before beginning the Requirement Layer.

==========================================================
OBJECTIVE
==========================================================

Treat the Canonical Layer as production-ready software.

Your responsibility is to verify that it fully complies with the Architecture Bible and is safe to freeze.

Only make changes if they are required for correctness, performance, maintainability or architecture compliance.

==========================================================
PHASE 1 — ARCHITECTURE AUDIT
==========================================================

Perform a complete architecture review.

Verify:

✓ Canonical is the ONLY transformation layer.
✓ Detection remains completely frozen.
✓ Processing has zero knowledge of physical schemas.
✓ No retailer-specific logic leaks downstream.
✓ No business logic exists inside UI.
✓ No duplicate parsing exists.
✓ All public contracts remain stable.
✓ No circular dependencies.
✓ Every module follows Single Responsibility Principle.

Identify every violation.

Fix only genuine violations.

==========================================================
PHASE 2 — CODE QUALITY REVIEW
==========================================================

Review every Canonical module.

Check for:

unused code

dead code

duplicate logic

unnecessary abstractions

large functions

incorrect module responsibilities

missing type hints

missing documentation

unsafe exception handling

unused imports

performance bottlenecks

Only refactor when it improves architecture or maintainability.

==========================================================
PHASE 3 — STREAMING REVIEW
==========================================================

The Architecture Bible is Streaming First.

Verify that:

large files do not require full DataFrame materialization

chunk processing works correctly

Canonical transformations operate on streamed data where practical

memory usage scales appropriately

Review engine.transform().

If the streaming implementation exists separately,

integrate it only if doing so does not break existing contracts.

Avoid introducing regressions.

==========================================================
PHASE 4 — INTEGRATION VALIDATION
==========================================================

Validate the entire pipeline.

IDataSource

↓

Detection

↓

Canonical

↓

Requirement Interface

Verify that Processing would receive ONLY:

CanonicalDataset

CanonicalMetadata

No physical columns

No layouts

No delimiters

No record types

No fixed-width structures

No multiline structures

==========================================================
PHASE 5 — BUSINESS SCENARIO TESTING
==========================================================

Validate Canonical against realistic retailer datasets.

Scenarios include:

Delimited POS

Fixed-width POS

Multiline POS

Mixed record types

Weight only

Units only

Mixed Weight + Units

Header/Trailer records

Missing UOM

Unknown UOM

Large datasets

Missing mandatory fields

Duplicate mappings

Schema changes between retailer versions

Ensure every scenario produces the expected CanonicalDataset.

==========================================================
PHASE 6 — PERFORMANCE REVIEW
==========================================================

Review performance.

Measure or estimate:

memory usage

chunk efficiency

large file scalability

transformation cost

preview generation

mapping performance

Identify obvious optimisation opportunities.

Implement only safe optimisations.

==========================================================
PHASE 7 — PREVIEW REVIEW
==========================================================

Verify Canonical Preview.

Ensure it displays ONLY business fields.

Never expose retailer column names.

Never expose physical layouts.

Never expose record types.

Preview must exactly represent what Processing receives.

==========================================================
PHASE 8 — METADATA REVIEW
==========================================================

Verify CanonicalMetadata contains complete transformation traceability.

Confirm metadata includes:

mapped columns

ignored columns

confidence scores

warnings

transformation log

flatten strategy

quantity strategy

UOM strategy

validation summary

record counts

source format

==========================================================
PHASE 9 — TEST REVIEW
==========================================================

Run the complete test suite.

All existing tests must pass.

Review coverage.

Add tests only where meaningful gaps exist.

Focus especially on:

streaming

flattening

fixed-width

multiline

schema generation

metadata

validation

==========================================================
PHASE 10 — DOCUMENTATION
==========================================================

Update Canonical documentation.

Document:

module responsibilities

public contracts

pipeline

transformation flow

extension points

developer guidelines

Ensure future developers understand where new logic belongs.

==========================================================
FREEZE CHECKLIST
==========================================================

The Canonical Layer can be frozen ONLY if ALL conditions are true.

✓ Architecture audit passed

✓ No downstream physical schema leakage

✓ Streaming architecture validated

✓ Fixed-width validated

✓ Multiline validated

✓ Hierarchy flattening validated

✓ Quantity normalization validated

✓ UOM normalization validated

✓ Metadata validated

✓ Preview validated

✓ Validation validated

✓ Integration tests passed

✓ Unit tests passed

✓ Performance acceptable

✓ Documentation complete

✓ No remaining architecture violations

==========================================================
FINAL DELIVERABLES
==========================================================

Produce a Sprint 3C Freeze Report containing:

1. Architecture Audit
2. Code Quality Findings
3. Streaming Review
4. Performance Review
5. Integration Review
6. Business Scenario Results
7. Test Results
8. Remaining Risks (if any)
9. Freeze Recommendation

The recommendation must be one of:

READY TO FREEZE

or

NOT READY TO FREEZE

If NOT READY TO FREEZE:

- Explain every blocker.
- Fix all blockers if possible.
- Re-run validation.

Only recommend READY TO FREEZE when the Canonical Layer requires no further architectural work.

Finally:

1. Commit any approved changes with a meaningful commit message.
2. Push to the current feature branch.
3. If the freeze recommendation is READY TO FREEZE, tag the repository as:

v2-sprint3-final

The Canonical Layer should then be considered immutable except for future bug fixes.
