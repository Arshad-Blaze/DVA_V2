You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is UI Sprint 4A — Canonical Mapping Studio.

Prerequisites

✓ UI Foundation
✓ Project Workspace
✓ Connection Workspace
✓ Persistence Foundation
✓ Detection Workspace

Backend Canonical Layer is COMPLETE and FROZEN.

DO NOT modify backend Canonical implementation.

The UI must consume Canonical public contracts only.

==========================================================
OBJECTIVE
==========================================================

Build the Canonical Mapping Studio.

This is NOT a spreadsheet.

This is NOT an Excel mapper.

This is a Business Schema Builder.

The user should feel like they are translating a retailer's physical file into the DVA Business Model.

The workspace should guide the user through mapping rather than overwhelming them with configuration.

==========================================================
USER JOURNEY
==========================================================

Detection Accepted

↓

Review Physical Columns

↓

Review Suggested Business Mappings

↓

Adjust Mapping (if required)

↓

Resolve Quantity

↓

Resolve UOM

↓

Review Business Schema

↓

Save Mapping

↓

Continue

==========================================================
LAYOUT
==========================================================

+-----------------------------------------------------------------------+
| Canonical Mapping Studio                                              |
+-----------------------------------------------------------------------+

Detection Summary

-----------------------------------------------------------------------

Physical Schema Explorer

-----------------------------------------------------------------------

Business Schema Builder

-----------------------------------------------------------------------

Mapping Confidence

-----------------------------------------------------------------------

Quantity & UOM Resolution

-----------------------------------------------------------------------

Mapping Inspector

-----------------------------------------------------------------------

Transformation Summary

-----------------------------------------------------------------------

Actions

Auto Map

Reset

Save Mapping

Continue

==========================================================
SECTION 1 — DETECTION SUMMARY
==========================================================

Display

Detected Format

Delimiter

Encoding

Header

Record Types

Layout

Confidence

Accepted Timestamp

Read-only.

==========================================================
SECTION 2 — PHYSICAL SCHEMA EXPLORER
==========================================================

Display all detected columns.

Each column shows

Name

Sample Values

Detected Type

Null %

Unique %

Confidence

Original Position

Allow searching.

Allow sorting.

Allow filtering.

This represents the retailer schema.

==========================================================
SECTION 3 — BUSINESS SCHEMA BUILDER
==========================================================

Display the DVA Canonical Business Schema.

Examples

Store

Store Name

UPC

Description

Category

Brand

Department

Quantity

UOM

Price

Sales

Date

Promotion

Currency

Tax

Each business field should show

Purpose

Required/Optional

Mapped Physical Column

Confidence

Status

==========================================================
SECTION 4 — SMART MAPPING
==========================================================

Invoke Canonical Layer suggestions.

Show

Suggested Match

Confidence

Reason

Example

Retailer

STORE_ID

↓

Business

Store

Confidence

99%

Reason

"Name similarity and sample values."

Allow

Accept

Reject

Manual Select

==========================================================
SECTION 5 — MAPPING STUDIO
==========================================================

Professional mapping experience.

Support

Dropdown mapping

Drag-and-drop (architecture ready)

Search

Quick assign

Bulk assign

Clear mapping

Swap mapping

Every mapping clearly shows

Physical

↓

Business

==========================================================
SECTION 6 — QUANTITY RESOLUTION
==========================================================

Visualize

Weight Column

Units Column

Detected Strategy

Effective Quantity

Explain

Weight preferred

Units fallback

Display

Current Strategy

Reason

Resolved Quantity

Read-only unless override needed.

==========================================================
SECTION 7 — UOM
==========================================================

Display

Detected UOM

Confidence

Sample Values

Normalization Status

Allow override only when necessary.

==========================================================
SECTION 8 — MAPPING CONFIDENCE
==========================================================

Show

Overall Mapping Confidence

Required Fields

Optional Fields

Mapped %

Unmapped %

Confidence Breakdown

Visual dashboard.

==========================================================
SECTION 9 — TRANSFORMATION SUMMARY
==========================================================

Display

Mapped Columns

Ignored Columns

Auto Mapped

Manual Mapped

Required Missing

Transformation Strategy

Ready for Validation

==========================================================
SECTION 10 — MAPPING INSPECTOR
==========================================================

Persistent side panel.

Display

Selected Physical Column

Sample Values

Detected Type

Suggested Business Fields

Mapping History

Confidence

Notes

==========================================================
SECTION 11 — ACTIONS
==========================================================

Buttons

Auto Map

Clear Mapping

Reset Suggestions

Save Mapping

Export Mapping

Continue

Continue disabled until required mappings complete.

==========================================================
PROGRESSIVE DISCLOSURE
==========================================================

Do NOT show all fields immediately.

Default

Business Essentials

Store

UPC

Description

Quantity

Sales

Date

Advanced

▼

Category

Brand

Department

Promotion

Currency

Tax

Future Custom Fields

==========================================================
REUSABLE WIDGETS
==========================================================

Create

Mapping Card

Business Field Card

Physical Field Card

Confidence Badge

Mapping Connector

Schema Explorer

Business Explorer

Transformation Summary

Inspector Panel

==========================================================
USER EXPERIENCE
==========================================================

Professional.

Minimal.

Modern.

Search-first.

Keyboard friendly.

Collapsible sections.

Sticky inspector.

Responsive.

==========================================================
DESIGN PRINCIPLES
==========================================================

Business First

Canonical First

Progressive Disclosure

No Spreadsheet UX

No Business Logic

Explain Every Suggestion

==========================================================
NON-NEGOTIABLE
==========================================================

UI NEVER

Maps columns

Resolves quantity

Calculates confidence

Builds canonical schema

Validates mapping

Transforms records

Canonical Layer owns all business intelligence.

UI only visualizes and collects user choices.

==========================================================
TESTING
==========================================================

Create tests covering

Schema explorer

Business schema

Auto mapping visualization

Manual mapping

Search

Filtering

Quantity display

UOM display

Inspector

Transformation summary

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

1. Canonical Mapping Studio Architecture

2. User Journey

3. Wireframes

4. Component Hierarchy

5. State Flow

6. Workspace Screenshots

7. Mapping Workflow

8. Widget Catalog

9. Test Summary

10. Regression Summary

11. Known Limitations

12. Future Enhancements

==========================================================
EXIT CRITERIA
==========================================================

✓ Detection summary complete

✓ Physical schema explorer complete

✓ Business schema builder complete

✓ Smart mapping visualization complete

✓ Mapping Studio complete

✓ Quantity section complete

✓ UOM section complete

✓ Mapping confidence dashboard complete

✓ Transformation summary complete

✓ Inspector complete

✓ UI tests passing

✓ Backend regression passing

✓ Architecture review passed

✓ No business logic in UI

Commit

Push

Tag

v2-ui-canonical-mapping

Write a Completion Report

Freeze UI Sprint 4A. 
