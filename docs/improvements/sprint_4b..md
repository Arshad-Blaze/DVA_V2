You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 4B — Requirement Intelligence.

Sprint 4A has already been completed.

DO NOT redesign the Requirement Layer.

Extend it with planning and intelligence capabilities.

==========================================================
OBJECTIVE
==========================================================

Transform the Requirement Layer into the planning engine of the platform.

Requirement must determine WHAT should happen.

Operation must determine HOW it happens.

==========================================================
NEW RESPONSIBILITIES
==========================================================

Requirement must analyse:

Business objective

Dataset readiness

Required inputs

Missing inputs

Capabilities

Workflow recommendation

Execution planning

==========================================================
1. Business Goal Analysis
==========================================================

Support business goals such as:

Raw Review

Validation

Format Change

Migration

Comparison

Reporting

Aggregation

Calculation

Determine the intended business objective.

==========================================================
2. Capability Detection
==========================================================

Determine automatically:

Can Aggregate

Can Calculate

Can Compare

Can Validate

Can Migrate

Can Report

Can Review

Return capability matrix.

==========================================================
3. Requirement Validation
==========================================================

Validate:

Baseline dataset available

Comparison dataset available

Canonical mapping complete

Mandatory fields present

Configuration complete

Required user inputs supplied

Dependencies satisfied

Produce structured validation results.

==========================================================
4. Recommendation Engine
==========================================================

Recommend:

Best workflow

Best processing mode

Aggregation strategy

Calculation strategy

Warnings

Missing prerequisites

Expected outputs

Provide confidence score.

==========================================================
5. Execution Planning
==========================================================

Build an execution plan.

Example:

Analyse

↓

Aggregate

↓

Calculate

↓

Validate

↓

Generate Report

↓

Export

Operation Layer should execute this plan.

==========================================================
6. Enhanced OperationContext
==========================================================

Expand OperationContext to include:

Business Goal

Capability Matrix

Validation Results

Execution Plan

Recommended Workflow

Required Inputs

Missing Inputs

Expected Outputs

Warnings

Confidence

==========================================================
7. Requirement Metadata
==========================================================

Add:

Business readiness

Capability summary

Planning decisions

Recommendation reasoning

Validation trace

==========================================================
8. Integration
==========================================================

Validate pipeline:

Canonical

↓

Requirement Analysis

↓

Capability Detection

↓

Execution Plan

↓

Operation

Ensure Operation receives a complete execution plan rather than making business decisions itself.

==========================================================
NON-NEGOTIABLE RULES
==========================================================

Requirement still performs NO aggregation.

Requirement still performs NO calculations.

Requirement still performs NO report generation.

Requirement performs planning ONLY.

==========================================================
TESTING
==========================================================

Add tests covering:

Business goal detection

Capability detection

Requirement validation

Recommendation engine

Execution planning

Enhanced OperationContext

Integration

Edge cases

==========================================================
EXIT CRITERIA
==========================================================

Requirement should answer:

What is the user trying to accomplish?

Is it possible?

What is missing?

What is recommended?

What workflow should execute?

Operation should only execute the supplied plan.

==========================================================
FINAL DELIVERABLES
==========================================================

Produce a Sprint 4B Completion Report including:

Architecture review

Capability matrix

Planning engine summary

Recommendation engine summary

Execution planning summary

Test results

Remaining risks

Freeze recommendation

If architecture compliance passes:

Commit

Push

Tag:

v2-sprint4-final

Freeze the Requirement Layer.
