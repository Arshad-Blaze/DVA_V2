You are continuing the DVA Platform rebuild.

IMPORTANT

This is Sprint 3B — Canonical Transformation Engine.

Sprint 3A (Canonical Foundation) has already been completed and validated.

DO NOT redesign or rewrite existing architecture.

DO NOT refactor working modules unless absolutely necessary.

Preserve all existing tests and architecture.

The goal is to COMPLETE the Canonical Layer so it can be frozen after validation.

==========================================================
CURRENT STATUS
==========================================================

Completed

✓ Contracts
✓ Physical → Canonical Mapping
✓ Confidence-based Mapping
✓ Type Coercion Foundation
✓ Quantity Resolution Foundation
✓ Canonical DataFrame
✓ Detection → Canonical Integration
✓ Existing Unit Tests Passing

Remaining work focuses ONLY on transformation responsibilities defined in the Architecture Bible.

==========================================================
ARCHITECTURE
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

Validation
↓

Output
↓

Flush

UI remains outside all business layers.

After Canonical, NO downstream layer may know anything about:

- retailer layouts
- physical columns
- fixed width
- multiline records
- record hierarchies
- delimiters

Canonical is the ONLY transformation boundary.

==========================================================
SPRINT 3B OBJECTIVES
==========================================================

Implement the remaining Canonical responsibilities.

==========================================================
1. Fixed Width Transformation Engine
==========================================================

Detection already provides:

- layout
- start positions
- lengths
- data types
- record types

Canonical must:

- slice fields
- trim values
- apply datatype conversion
- create canonical rows

Processing must never perform fixed-width parsing.

==========================================================
2. Record Hierarchy Flattening
==========================================================

Support retailer layouts such as

HDR
S
U
U
U
S
U
TRL

or

H
D
T

or any supported hierarchy.

Canonical must combine related records into a SINGLE logical business record.

Processing must never know hierarchical records existed.

==========================================================
3. Multiline Flattening
==========================================================

Support records spanning multiple physical lines.

Examples

U
Continuation
Continuation

↓

One canonical row.

Canonical owns all multiline logic.

==========================================================
4. Business Schema Builder
==========================================================

Produce a stable business schema independent of retailer format.

Typical business fields include:

Store
UPC
Description
Quantity
Sales
Weight
Date
Category
Department
Brand
UOM

Retailer-specific column names must disappear after this layer.

==========================================================
5. Quantity Normalization
==========================================================

Apply business rule:

IF Weight > 0

Quantity = Weight
QuantityType = WEIGHT

ELSE IF Units > 0

Quantity = Units
QuantityType = UNIT

ELSE

Quantity = 0
QuantityType = NONE

Downstream Processing should consume only the canonical Quantity field.

==========================================================
6. UOM Normalization
==========================================================

Normalize common UOM values such as:

KG
LB
EA
CT
G
OZ

Expose a single canonical UOM column.

If no UOM exists, handle gracefully.

==========================================================
7. Canonical Validation
==========================================================

Validate before data leaves Canonical.

Examples:

- missing mandatory business columns
- duplicate canonical mappings
- multiple physical columns mapped to one canonical field
- datatype issues
- invalid layouts
- inconsistent schemas

Return structured validation results.

Do not crash on recoverable issues.

==========================================================
8. Canonical Metadata
==========================================================

Produce metadata including:

Mapped columns

Ignored columns

Confidence scores

Warnings

Transformation log

Flatten strategy

Quantity strategy

UOM strategy

Record counts

Validation summary

Original format information

==========================================================
9. Canonical Preview
==========================================================

Preview ONLY business columns.

Never display physical retailer column names.

Preview should represent exactly what Processing will receive.

==========================================================
10. Streaming Canonical Dataset
==========================================================

Move toward streaming-first processing.

Avoid materializing the full dataset unless required.

Support generators, iterators or chunk-based pipelines where practical.

Design with multi-GB retailer files in mind.

==========================================================
NON-NEGOTIABLE ARCHITECTURE RULES
==========================================================

Detection executes exactly once.

Canonical is the only transformation layer.

Processing must never:

- parse files
- flatten records
- inspect retailer schemas
- resolve quantities
- normalize UOM
- interpret layouts

No Streamlit.

No UI logic.

No duplicate parsing.

No retailer-specific logic outside Canonical.

==========================================================
TESTING
==========================================================

Add comprehensive tests for:

✓ Fixed-width transformation
✓ Record hierarchy flattening
✓ Multiline flattening
✓ Business schema generation
✓ Quantity normalization
✓ UOM normalization
✓ Canonical validation
✓ Canonical metadata
✓ Canonical preview
✓ Streaming pipeline behaviour
✓ Large dataset scenarios
✓ Edge cases
✓ Invalid layouts
✓ Mixed retailer schemas

All existing tests must continue to pass.

==========================================================
ARCHITECTURE REVIEW
==========================================================

After implementation:

1. Perform a complete Architecture Bible compliance review.
2. Verify no physical schema leaks beyond Canonical.
3. Verify Processing receives only:
   - CanonicalDataset
   - CanonicalMetadata
4. Identify and fix any deviations.
5. Ensure the Canonical layer is fully self-contained.

==========================================================
EXIT CRITERIA
==========================================================

Sprint 3B is complete only when all of the following are true:

✓ Fixed-width transformation implemented
✓ Record hierarchy flattening implemented
✓ Multiline flattening implemented
✓ Business schema builder completed
✓ Quantity normalization completed
✓ UOM normalization completed
✓ Canonical validation completed
✓ Canonical metadata completed
✓ Canonical preview completed
✓ Streaming canonical dataset implemented
✓ Existing tests passing
✓ New tests passing
✓ Integration tests passing
✓ Architecture review passed
✓ No business logic outside Canonical
✓ No physical schema leakage

Finally:

1. Produce a Sprint 3B Completion Report detailing:
   - Features implemented
   - Test results
   - Architecture compliance
   - Performance considerations
   - Remaining technical risks (if any)

2. If all exit criteria are satisfied, commit the changes with a clear commit message, push them to the current feature branch, and mark the Canonical Layer as ready to be frozen.
