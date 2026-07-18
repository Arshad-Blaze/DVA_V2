You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is UI Sprint 4B — Business Preview Studio & Canonical Validation.

UI Sprint 4A (Canonical Mapping Studio) is COMPLETE and FROZEN.

Backend Canonical Layer is COMPLETE and FROZEN.

DO NOT modify backend code.

This workspace consumes Canonical Layer public contracts only.

==========================================================
OBJECTIVE
==========================================================

Build the Business Preview Studio.

This is NOT another mapping screen.

This is the user's final confidence checkpoint before Processing.

The purpose is to answer:

"Is this retailer data correctly transformed into the DVA Business Model?"

The workspace should make the user feel confident before continuing.

==========================================================
USER JOURNEY
==========================================================

Mapping Complete

↓

Business Preview

↓

Review Canonical Dataset

↓

Review Validation

↓

Review Transformation Quality

↓

Review Metadata

↓

Approve

↓

Continue to Requirement Workspace

==========================================================
WORKSPACE LAYOUT
==========================================================

+-----------------------------------------------------------------------+
| Business Preview Studio                                               |
+-----------------------------------------------------------------------+

Transformation Pipeline

-----------------------------------------------------------------------

Business Dataset Preview

-----------------------------------------------------------------------

Mapping Validation

-----------------------------------------------------------------------

Transformation Quality

-----------------------------------------------------------------------

Metadata Explorer

-----------------------------------------------------------------------

Warnings / Suggestions

-----------------------------------------------------------------------

Business Statistics

-----------------------------------------------------------------------

Actions

Approve

Back to Mapping

Export Preview

Continue

==========================================================
SECTION 1 — TRANSFORMATION PIPELINE
==========================================================

Visual pipeline

Physical File

↓

Detection

↓

Business Mapping

↓

Business Preview

↓

Ready for Processing

Highlight current stage.

==========================================================
SECTION 2 — SIDE-BY-SIDE COMPARISON
==========================================================

Split screen.

LEFT

Retailer Schema

Original Columns

Original Sample Values

RIGHT

Business Schema

Canonical Fields

Canonical Values

Example

STORE_ID

↓

Store

ITEM_CODE

↓

UPC

TOT_WGT

↓

Quantity

NET_PRICE

↓

Sales

Users should immediately understand the transformation.

==========================================================
SECTION 3 — BUSINESS DATASET PREVIEW
==========================================================

Display the Canonical Dataset.

Columns such as

Store

UPC

Description

Quantity

UOM

Sales

Category

Brand

Department

Promotion

Date

Currency

Tax

Use business names only.

Never display physical names.

Support

Filtering

Sorting

Searching

Column resizing

Pagination

==========================================================
SECTION 4 — MAPPING VALIDATION
==========================================================

Display

Required Fields

Mapped Fields

Optional Fields

Missing Fields

Duplicate Mappings

Ignored Columns

Quantity Strategy

UOM Strategy

Confidence

Clearly show

Passed

Warnings

Errors

==========================================================
SECTION 5 — TRANSFORMATION QUALITY
==========================================================

Professional dashboard.

Examples

Overall Quality

Mapping Confidence

Required Coverage

Optional Coverage

Manual Mapping Count

Automatic Mapping Count

Ignored Columns

Missing Columns

Overall Readiness

Display visually.

==========================================================
SECTION 6 — BUSINESS STATISTICS
==========================================================

Display

Rows

Columns

Stores

Unique UPCs

Categories

Brands

Departments

Date Range

Null %

Duplicate %

Business Completeness

Consume backend statistics only.

==========================================================
SECTION 7 — METADATA EXPLORER
==========================================================

Display

Transformation Strategy

Applied Rules

Quantity Strategy

UOM Strategy

Ignored Columns

Transformation Time

Canonical Version

Schema Version

Warnings

==========================================================
SECTION 8 — WARNINGS
==========================================================

Examples

Missing Required Field

Low Mapping Confidence

Duplicate Business Field

Unused Retailer Column

Quantity Fallback Used

Unknown UOM

Mixed Units

Warnings should explain

Problem

Impact

Recommendation

==========================================================
SECTION 9 — APPROVAL PANEL
==========================================================

Before Processing

Display checklist

✓ Mapping Complete

✓ Validation Passed

✓ Required Fields Present

✓ Business Schema Ready

✓ Canonical Dataset Generated

Allow

Approve

Reject

Back to Mapping

==========================================================
SECTION 10 — ACTIONS
==========================================================

Buttons

Back to Mapping

Export Preview

Export Mapping

Approve

Continue

Continue enabled only after approval.

==========================================================
INSPECTOR PANEL
==========================================================

Display

Current Mapping

Selected Business Field

Transformation Details

Confidence

Warnings

Metadata

==========================================================
STATUS BAR
==========================================================

Display

Workspace

Readiness

Rows

Business Fields

Validation Status

==========================================================
REUSABLE WIDGETS
==========================================================

Create

Pipeline Widget

Comparison Viewer

Business Preview Table

Quality Dashboard

Validation Checklist

Metadata Card

Transformation Card

Warning Panel

Approval Card

==========================================================
DESIGN PRINCIPLES
==========================================================

Business First

Explain Everything

Confidence Before Processing

No Hidden Transformations

Professional Data Review

==========================================================
NON-NEGOTIABLE
==========================================================

UI NEVER

Builds Canonical Dataset

Validates Mappings

Calculates Statistics

Calculates Confidence

Transforms Data

Backend Canonical Layer owns all transformation.

UI only visualizes results.

==========================================================
USER EXPERIENCE
==========================================================

Professional.

Modern.

Readable.

Minimal.

Large datasets should remain responsive.

Support

Sticky headers

Pinned columns

Search

Filter

Export

Keyboard navigation

==========================================================
TESTING
==========================================================

Create tests covering

Business preview

Comparison viewer

Validation display

Quality dashboard

Metadata explorer

Warnings

Approval workflow

Export preview

Navigation

Inspector

Accessibility

Responsive layout

==========================================================
REGRESSION
==========================================================

Run

Backend Tests

UI Tests

Regression Tests

Architecture Tests

Contract Tests

Performance Tests

End-to-End Tests

Fix every regression.

Every bug discovered must receive a permanent regression test.

==========================================================
DELIVERABLES
==========================================================

Produce

1. Business Preview Studio Architecture

2. User Journey

3. Wireframes

4. Component Hierarchy

5. State Flow

6. Workspace Screenshots

7. Transformation Flow

8. Widget Catalog

9. Test Summary

10. Regression Summary

11. Known Limitations

12. Future Enhancements

==========================================================
EXIT CRITERIA
==========================================================

✓ Pipeline visualization complete

✓ Side-by-side comparison complete

✓ Business dataset preview complete

✓ Mapping validation display complete

✓ Quality dashboard complete

✓ Metadata explorer complete

✓ Warnings complete

✓ Approval workflow complete

✓ UI tests passing

✓ Backend regression passing

✓ Architecture review passed

✓ No business logic in UI

Commit

Push

Tag

v2-ui-business-preview

Freeze UI Sprint 4B and write completion report.
