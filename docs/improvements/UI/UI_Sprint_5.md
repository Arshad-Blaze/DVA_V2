You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is UI Sprint 5 — Analysis Planner.

Prerequisites

✓ UI Foundation
✓ Project Workspace
✓ Connection Workspace
✓ Persistence Foundation
✓ Detection Workspace
✓ Business Mapping Studio
✓ Business Preview Studio

Backend Requirement Layer is COMPLETE and FROZEN.

DO NOT modify backend Requirement implementation.

The UI consumes Requirement Layer public contracts only.

==========================================================
OBJECTIVE
==========================================================

Build the Analysis Planner.

This workspace helps users define WHAT they want to accomplish.

The user should never think about backend execution.

Instead they should answer business questions.

The Requirement Layer converts these business goals into an OperationContext.

==========================================================
USER JOURNEY
==========================================================

Business Preview Approved

↓

Select Business Goal

↓

Review Recommended Workflow

↓

Review Capabilities

↓

Review Missing Inputs

↓

Review Execution Plan

↓

Confirm Plan

↓

Continue to Execution Planner

==========================================================
WORKSPACE LAYOUT
==========================================================

+--------------------------------------------------------------------+
| Analysis Planner                                                   |
+--------------------------------------------------------------------+

Business Goal

---------------------------------------------------------------------

Recommended Workflow

---------------------------------------------------------------------

Capability Matrix

---------------------------------------------------------------------

Missing Inputs

---------------------------------------------------------------------

Execution Plan

---------------------------------------------------------------------

Expected Outputs

---------------------------------------------------------------------

Warnings

---------------------------------------------------------------------

Actions

Generate Plan

Modify Goal

Confirm Plan

Continue

==========================================================
SECTION 1 — BUSINESS GOAL
==========================================================

Present goals as large cards.

Examples

Retailer Onboarding

Format Change

Migration Validation

Raw Data Review

Aggregate Only

Aggregate + Calculate

Store Validation

Item Validation

Custom Analysis

Each goal should include

Description

Typical use cases

Expected outputs

Estimated execution complexity

==========================================================
SECTION 2 — SMART RECOMMENDATION
==========================================================

Invoke Requirement Layer recommendation engine.

Display

Recommended Workflow

Confidence

Reason

Alternative Workflows

Why recommended

Allow

Accept Recommendation

Choose Different Goal

==========================================================
SECTION 3 — CAPABILITY MATRIX
==========================================================

Display capabilities available.

Examples

✓ Store Validation

✓ Item Validation

✓ Aggregation

✓ Calculations

✓ Migration

✓ Format Comparison

✓ Business Statistics

Grey out unsupported capabilities.

Explain why.

==========================================================
SECTION 4 — MISSING INPUTS
==========================================================

Display requirements still needed.

Examples

Reference Dataset Required

Target Dataset Missing

Output Directory Missing

Configuration Required

Connection Missing

Project Incomplete

Provide direct navigation links.

==========================================================
SECTION 5 — EXECUTION PLAN
==========================================================

Visual execution pipeline.

Example

Load Data

↓

Aggregate

↓

Calculate

↓

Validate

↓

Generate Reports

↓

Export

Display estimated execution stages only.

==========================================================
SECTION 6 — EXPECTED OUTPUTS
==========================================================

Show what the user will receive.

Examples

Excel Report

CSV

Validation Summary

Business Statistics

Store Report

Item Report

Execution Summary

==========================================================
SECTION 7 — EXECUTION ESTIMATES
==========================================================

Display

Estimated Runtime

Processing Complexity

Memory Estimate

Streaming

Expected Report Count

Expected Validation Rules

Consume backend estimates only.

==========================================================
SECTION 8 — WARNINGS
==========================================================

Examples

Large Dataset

Reference Dataset Missing

High Memory Usage

Migration Mode

Low Confidence Mapping

Configuration Missing

Explain

Impact

Recommendation

==========================================================
SECTION 9 — READINESS DASHBOARD
==========================================================

Display

Project Ready

Connection Ready

Detection Ready

Business Mapping Ready

Business Preview Approved

Requirement Complete

Overall Readiness

Visual indicators

Green

Yellow

Red

==========================================================
SECTION 10 — ACTIONS
==========================================================

Buttons

Back to Business Preview

Generate Plan

Accept Recommendation

Modify Goal

Confirm Plan

Continue

Continue enabled only after confirmation.

==========================================================
INSPECTOR PANEL
==========================================================

Display

Current Goal

Recommendation

Workflow

Confidence

Warnings

Missing Inputs

==========================================================
STATUS BAR
==========================================================

Display

Current Workspace

Business Goal

Execution Mode

Readiness

==========================================================
REUSABLE WIDGETS
==========================================================

Create

Business Goal Card

Recommendation Card

Capability Matrix

Execution Timeline

Readiness Gauge

Output Preview Card

Warning Banner

Execution Estimate Card

==========================================================
DESIGN PRINCIPLES
==========================================================

Business Language

No Technical Jargon

Goal Driven

Explain Recommendations

Minimal Configuration

Professional Workflow

==========================================================
NON-NEGOTIABLE
==========================================================

UI NEVER

Plans execution

Calculates recommendations

Determines capabilities

Builds OperationContext

Requirement Layer owns all planning logic.

UI only visualizes and gathers user choices.

==========================================================
TESTING
==========================================================

Create tests covering

Goal selection

Recommendation display

Capability matrix

Missing input display

Execution plan visualization

Expected outputs

Readiness dashboard

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

Every discovered bug must receive a permanent regression test.

==========================================================
DELIVERABLES
==========================================================

Produce

1. Analysis Planner Architecture

2. User Journey

3. Wireframes

4. Component Hierarchy

5. State Flow

6. Workspace Screenshots

7. Planning Workflow

8. Widget Catalog

9. Test Summary

10. Regression Summary

11. Known Limitations

12. Future Enhancements

==========================================================
EXIT CRITERIA
==========================================================

✓ Goal selection complete

✓ Recommendation visualization complete

✓ Capability matrix complete

✓ Missing input visualization complete

✓ Execution plan visualization complete

✓ Expected outputs complete

✓ Readiness dashboard complete

✓ UI tests passing

✓ Backend regression passing

✓ Architecture review passed

✓ No business logic in UI

Commit

Push

Tag

v2-ui-analysis-planner

Freeze UI Sprint 5.
