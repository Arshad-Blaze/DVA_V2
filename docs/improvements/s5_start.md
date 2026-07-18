You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is Sprint 5 — Operation Layer.

The following layers are FROZEN and MUST NOT be modified except for critical bug fixes:

✓ Connection
✓ Detection
✓ Canonical
✓ Requirement

The Operation Layer must strictly follow the Architecture Bible.

==========================================================
OBJECTIVE
==========================================================

The Operation Layer is the orchestration engine.

It receives an OperationContext from the Requirement Layer and executes the supplied ExecutionPlan.

The Operation Layer DOES NOT:

- make business decisions
- determine workflows
- aggregate data
- calculate values
- validate business rules
- generate reports

Its only responsibility is orchestration.

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

Operation   ← YOU ARE HERE

↓

Processing

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

OperationContext

CanonicalDataset

CanonicalMetadata

==========================================================
OUTPUT
==========================================================

ExecutionResult

ExecutionMetadata

OperationLog

==========================================================
RESPONSIBILITIES
==========================================================

1. Execution Engine

Receive OperationContext.

Read ExecutionPlan.

Execute steps sequentially.

Maintain execution state.

Return ExecutionResult.

==========================================================
2. Workflow Orchestrator
==========================================================

Support workflows produced by Requirement.

Examples:

review

aggregate_report

aggregate_calculate_report

validate

compare

migration

report

Operation NEVER chooses a workflow.

Requirement already made that decision.

==========================================================
3. Step Dispatcher
==========================================================

Dispatch each ExecutionStep to the correct downstream layer.

Examples:

Aggregate

↓

Processing Layer

Validate

↓

Validation Layer

Report

↓

Output Layer

Export

↓

Output Layer

Operation does NOT implement those operations.

==========================================================
4. Execution State
==========================================================

Maintain execution status.

Support:

Pending

Running

Completed

Skipped

Failed

Cancelled

Track current step.

Track completed steps.

Track failures.

==========================================================
5. Progress Tracking
==========================================================

Track:

Current step

Progress %

Elapsed time

Remaining steps

Warnings

Messages

Expose progress for UI.

==========================================================
6. Error Handling
==========================================================

Handle execution failures.

Support:

Retryable errors

Fatal errors

Partial completion

Graceful abort

Continue when allowed.

Stop when required.

==========================================================
7. Retry Policy
==========================================================

Implement configurable retry policy.

Support:

Retry count

Retry delay

Retry conditions

Record retry history.

==========================================================
8. Logging
==========================================================

Maintain structured execution logs.

Log:

Step started

Step completed

Duration

Errors

Warnings

Retry events

Final status

==========================================================
9. Operation Metadata
==========================================================

Generate metadata including:

Workflow executed

Steps completed

Execution duration

Execution statistics

Warnings

Errors

Final outcome

==========================================================
10. Cancellation Support
==========================================================

Support cancellation.

Execution should terminate safely.

Return partial status.

Preserve completed work.

==========================================================
NON-NEGOTIABLE ARCHITECTURE RULES
==========================================================

Operation performs NO aggregation.

Operation performs NO calculations.

Operation performs NO business validation.

Operation performs NO report generation.

Operation performs NO retailer-specific logic.

Operation never modifies CanonicalDataset.

Operation never modifies OperationContext.

Operation only orchestrates.

==========================================================
PUBLIC CONTRACTS
==========================================================

ExecutionResult

ExecutionMetadata

OperationLog

ExecutionState

ExecutionStepResult

Keep contracts stable.

==========================================================
DESIGN PRINCIPLES
==========================================================

Single Responsibility

Command Pattern

Strategy Pattern where appropriate

Dependency Injection

No circular dependencies

No UI imports

No Streamlit

Small reusable modules

==========================================================
SUGGESTED MODULES
==========================================================

engine.py

dispatcher.py

executor.py

state.py

progress.py

retry.py

logging.py

contracts.py

exceptions.py

__init__.py

==========================================================
TESTING
==========================================================

Create comprehensive tests covering:

Execution engine

Workflow orchestration

Step dispatching

Progress tracking

Execution state transitions

Retry logic

Cancellation

Logging

Error handling

Execution metadata

Integration with Requirement

Mock Processing layer

Mock Validation layer

Mock Output layer

Large execution plans

Edge cases

==========================================================
INTEGRATION
==========================================================

Validate:

Requirement

↓

Operation

↓

(Mock Processing)

↓

(Mock Validation)

↓

(Mock Output)

Verify that Operation correctly dispatches work without performing the work itself.

==========================================================
ARCHITECTURE REVIEW
==========================================================

Verify:

Operation never makes business decisions.

Operation never aggregates.

Operation never validates.

Operation never reports.

Operation only executes the supplied ExecutionPlan.

Ensure all responsibilities remain inside the correct downstream layers.

==========================================================
EXIT CRITERIA
==========================================================

✓ Execution engine implemented

✓ Workflow orchestrator implemented

✓ Dispatcher implemented

✓ Progress tracking implemented

✓ Execution state management implemented

✓ Retry policy implemented

✓ Structured logging implemented

✓ Error handling implemented

✓ Cancellation support implemented

✓ Metadata implemented

✓ Unit tests passing

✓ Integration tests passing

✓ Architecture review passed

✓ No violations of frozen layers

==========================================================
FINAL DELIVERABLES
==========================================================

Produce a Sprint 5 Completion Report including:

1. Architecture summary

2. Execution engine overview

3. Workflow orchestration summary

4. Dispatcher design

5. Progress tracking summary

6. Retry strategy

7. Logging strategy

8. Error handling strategy

9. Test results

10. Remaining risks

If all exit criteria are satisfied:

Commit changes

Push to the current feature branch

Tag:

v2-sprint5-complete

Freeze the Operation Layer.
