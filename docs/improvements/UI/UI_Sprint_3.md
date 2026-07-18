You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is UI Sprint 3 — Detection Workspace & Analysis Studio.

Prerequisites:

✓ UI Foundation complete
✓ Project Workspace complete
✓ Connection Workspace complete
✓ Persistence Foundation complete

Backend Detection Layer is COMPLETE and FROZEN.

DO NOT modify Detection Layer.

The UI MUST consume Detection public contracts only.

==========================================================
OBJECTIVE
==========================================================

Build the Detection Workspace.

This is NOT a configuration form.

It is an interactive data analysis workspace.

Users should understand:

• What was detected
• Why it was detected
• How confident the detector is
• What can be overridden
• What will happen next

The workspace should feel closer to an IDE or Data Profiling tool than a settings page.

==========================================================
WORKSPACE GOALS
==========================================================

The Detection Workspace should guide users through:

Connection
↓

Raw File Inspection
↓

Automatic Detection
↓

Review Results
↓

Optional Manual Overrides
↓

Validation
↓

Accept Detection
↓

Continue to Canonical Workspace

==========================================================
LAYOUT
==========================================================

+---------------------------------------------------------------------+
| Detection Workspace                                                  |
+---------------------------------------------------------------------+

Connection Summary

-----------------------------------------------------------------------

Raw File Preview

-----------------------------------------------------------------------

Automatic Detection Results

-----------------------------------------------------------------------

Confidence Panel

-----------------------------------------------------------------------

Warnings / Suggestions

-----------------------------------------------------------------------

Manual Override

-----------------------------------------------------------------------

Detection Timeline

-----------------------------------------------------------------------

Actions

Retry

Validate

Accept

Continue

=======================================================================
SECTION 1 — CONNECTION SUMMARY
=======================================================================

Display

Project

Connection

Selected Files

Directory

Connection Type

File Count

Total Size

Selected File

Refresh Button

Open Connection Workspace

==========================================================
SECTION 2 — RAW FILE PREVIEW
==========================================================

Display the first lines exactly as received.

NO parsing.

NO formatting.

NO canonical mapping.

NO processing.

This is the physical file.

Support

Line numbers

Horizontal scrolling

Monospace font

Syntax highlighting (optional)

File encoding display

Record count estimate

Allow switching between selected files.

==========================================================
SECTION 3 — AUTOMATIC DETECTION
==========================================================

Invoke Detection Layer.

Display results in organized cards.

Examples

Detected Format

Delimited

Fixed Width

Multiline

Mixed Record Types

Delimiter

Encoding

Header

Trailer

Record Types

Start Line

Confidence

Layout

Schema

Each item should show

Value

Confidence

Explanation

==========================================================
SECTION 4 — DETECTION CONFIDENCE
==========================================================

Professional confidence visualization.

Examples

Overall Confidence

Delimiter Confidence

Header Confidence

Encoding Confidence

Layout Confidence

Record Type Confidence

Use progress bars or gauges.

Color coding

Green

Yellow

Red

==========================================================
SECTION 5 — EXPLANATIONS
==========================================================

Every detected value should answer

WHY?

Example

Header Detected

Confidence

98%

Reason

"Row 1 contains unique textual values matching column naming patterns."

Users should understand detection.

==========================================================
SECTION 6 — WARNINGS
==========================================================

Examples

Low confidence

Multiple delimiters detected

Possible multiline file

Unknown encoding

Duplicate headers

Missing trailer

Mixed record types

Allow users to click a warning for details.

==========================================================
SECTION 7 — MANUAL OVERRIDES
==========================================================

Allow override ONLY for:

Delimiter

Encoding

Header row

Start line

Layout

Record types

Override should NEVER rerun custom logic.

It should simply update Detection configuration.

Clearly distinguish

Detected Value

User Override

Provide "Reset to Auto Detect".

==========================================================
SECTION 8 — DETECTION TIMELINE
==========================================================

Display execution steps.

Example

✓ File Loaded

✓ Sample Read

✓ Encoding Detected

✓ Delimiter Detected

✓ Header Detected

✓ Layout Detected

✓ Detection Complete

Useful for troubleshooting.

==========================================================
SECTION 9 — ACTIONS
==========================================================

Buttons

Retry Detection

Validate Detection

Accept Detection

Continue to Canonical

Continue disabled until detection accepted.

==========================================================
INSPECTOR PANEL
==========================================================

Display

Current File

Detection Status

Confidence Summary

Warnings

Detection Duration

Sample Size

==========================================================
STATUS BAR
==========================================================

Display

Current Workspace

Detection Status

Selected File

Progress

Execution Time

==========================================================
USER EXPERIENCE
==========================================================

Support

Collapsible sections

Expandable cards

Tooltips

Search

Copy values

Export detection report (JSON)

Keyboard shortcuts

Loading indicators

==========================================================
WIDGETS
==========================================================

Create reusable widgets

Confidence Card

Detection Result Card

Warning Banner

Explanation Panel

Timeline

Raw Preview Viewer

Status Badge

Metric Tile

Section Header

==========================================================
DESIGN PRINCIPLES
==========================================================

Workspace Driven

Read-only Analysis

Manual Overrides

Transparent Detection

No Hidden Decisions

No Business Logic

==========================================================
NON-NEGOTIABLE RULES
==========================================================

UI NEVER

Detects files

Reads files directly

Parses data

Calculates confidence

Infers layouts

Processes records

The Detection Layer owns all intelligence.

UI only visualizes and collects overrides.

==========================================================
TESTING
==========================================================

Create tests covering

Workspace loading

Detection invocation

Raw preview rendering

Confidence display

Warnings

Override UI

Timeline

Inspector

Status bar

Navigation

Export detection report

Accessibility

Responsive layout

==========================================================
REGRESSION
==========================================================

Run the complete platform quality pipeline.

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

1. Detection Workspace Architecture

2. User Journey

3. Wireframes

4. Component Hierarchy

5. State Flow Diagram

6. Workspace Screenshots

7. Detection UI Flow

8. Widget Catalog

9. Test Summary

10. Regression Summary

11. Known Limitations

12. Future Enhancements

==========================================================
EXIT CRITERIA
==========================================================

✓ Detection Workspace complete

✓ Raw Preview complete

✓ Detection visualization complete

✓ Confidence dashboard complete

✓ Explanations complete

✓ Warnings complete

✓ Manual overrides complete

✓ Timeline complete

✓ Inspector complete

✓ Status bar integration complete

✓ UI tests passing

✓ Backend regression passing

✓ Architecture review passed

✓ No business logic in UI

Commit

Push

Tag

v2-ui-detection-workspace

Freeze UI Sprint 3.
