You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is UI Sprint 1 — Application Shell & Workspace Framework.

The backend architecture is COMPLETE and FROZEN.

DO NOT modify backend code except for confirmed bug fixes discovered during regression testing.

The UI is a completely separate architecture.

The UI must consume backend public contracts only.

It must NEVER contain business logic.

==========================================================
OBJECTIVE
==========================================================

Build the UI Foundation for the DVA Platform.

This sprint does NOT implement Connection, Detection, Processing or Reports.

Instead, it builds the application shell that every future workspace will use.

Think of this as building Visual Studio Code before building its editors.

==========================================================
DESIGN PHILOSOPHY
==========================================================

Target inspiration:

Visual Studio Code

Databricks

Power BI Desktop

Azure Data Factory

NOT a typical Streamlit demo.

The application should feel like a professional enterprise desktop application.

Clean.

Minimal.

Modern.

Fast.

Workspace driven.

==========================================================
UI ARCHITECTURE
==========================================================

Create a dedicated UI architecture completely separated from backend layers.

Suggested structure

ui/

    app.py

    shell/

        layout.py

        navigation.py

        sidebar.py

        header.py

        footer.py

        statusbar.py

        workspace_manager.py

    workspaces/

        home/

        connection/

        detection/

        canonical/

        requirement/

        operation/

        processing/

        validation/

        reports/

        settings/

        help/

    widgets/

        cards/

        tables/

        forms/

        previews/

        dialogs/

        notifications/

        progress/

        indicators/

        breadcrumbs/

    controllers/

        navigation_controller.py

        workspace_controller.py

        session_controller.py

    services/

        navigation_service.py

        notification_service.py

        session_service.py

        theme_service.py

    themes/

    assets/

    styles/

    icons/

==========================================================
APPLICATION LAYOUT
==========================================================

The application should have:

+------------------------------------------------------------+
| Header                                                     |
+-----------+--------------------------------+---------------+
|           |                                |               |
| Sidebar   |        Main Workspace          | Inspector     |
|           |                                |               |
|           |                                |               |
+-----------+--------------------------------+---------------+
| Status Bar                                                |
+------------------------------------------------------------+

==========================================================
HEADER
==========================================================

Display

Application logo

Project name

Current workspace

Execution status

Theme switch

Settings shortcut

==========================================================
SIDEBAR
==========================================================

Navigation should include

🏠 Home

📁 Projects

🔌 Connection

🔍 Detection

🧩 Canonical

📋 Requirement

⚙️ Operation

📊 Processing

✅ Validation

📑 Reports

⬇ Downloads

📜 History

⚙ Settings

❓ Help

Only Home should be functional.

The rest are placeholders.

==========================================================
MAIN WORKSPACE
==========================================================

Implement a reusable workspace framework.

Every future layer should plug into it.

Workspace should support

Title

Description

Toolbar

Content Area

Bottom Status

Action Buttons

No business logic.

==========================================================
RIGHT INSPECTOR
==========================================================

Persistent inspector panel.

Initially display

Session Information

Current Project

Selected Workspace

Notifications

Future layers will populate this.

==========================================================
STATUS BAR
==========================================================

Always visible.

Show

Current Layer

Session State

Memory Indicator

Execution Status

Streaming Status

Time

Version

==========================================================
HOME WORKSPACE
==========================================================

Create a professional dashboard.

Include cards

Create Project

Open Project

Recent Projects

Platform Status

Architecture Status

Backend Health

Frozen Layers

Current Version

Quick Start

Documentation

Recent Activity

Future Workflow

==========================================================
NAVIGATION FRAMEWORK
==========================================================

Implement reusable navigation.

Support

Navigation history

Active workspace

Disabled workspaces

Future breadcrumbs

Future deep linking

==========================================================
SESSION MANAGEMENT
==========================================================

Create session framework.

Track

Current Project

Current Workspace

Execution Status

User Preferences

Theme

Navigation History

No backend state.

==========================================================
NOTIFICATION FRAMEWORK
==========================================================

Support

Success

Warning

Error

Information

Progress

Future layers should reuse this.

==========================================================
PROGRESS FRAMEWORK
==========================================================

Create reusable progress system.

Support

Spinner

Progress Bar

Step Progress

Status Messages

Future execution progress.

==========================================================
THEME
==========================================================

Professional enterprise theme.

Light mode first.

Dark mode architecture ready.

Consistent spacing.

Rounded cards.

Subtle shadows.

Minimal colors.

Avoid bright gradients.

==========================================================
REUSABLE WIDGETS
==========================================================

Build reusable widgets.

Examples

Info Card

Metric Card

Section Header

Status Badge

Notification Banner

Empty State

Loading State

Toolbar

Search Box

Filter Bar

Action Button

Every future workspace should reuse them.

==========================================================
DESIGN PRINCIPLES
==========================================================

Single Responsibility

Component Based

Reusable Widgets

Workspace Driven

No Business Logic

No Backend Coupling

Controller Pattern

Service Pattern

==========================================================
NON-NEGOTIABLE RULES
==========================================================

UI NEVER performs

Detection

Parsing

Aggregation

Validation

Calculations

Report Generation

Business Rules

UI ONLY

Displays

Collects User Input

Shows Progress

Shows Results

==========================================================
RESPONSIVENESS
==========================================================

Support

Large monitors

Laptop screens

Collapsible sidebar

Resizable inspector

Scrollable workspace

==========================================================
ACCESSIBILITY
==========================================================

Keyboard navigation ready

Consistent spacing

Readable typography

Good contrast

Large click targets

==========================================================
TESTING
==========================================================

Create UI tests covering

Navigation

Workspace switching

Session management

Notification framework

Theme

Widget rendering

Sidebar

Status bar

Home workspace

Responsive layout

==========================================================
MANDATORY REGRESSION GATE
==========================================================

Run the complete platform quality pipeline.

Backend tests

Architecture tests

Regression tests

Contract tests

Performance tests

End-to-End tests

PLUS

UI tests

Fix any regressions before completion.

==========================================================
DELIVERABLES
==========================================================

Produce

1. UI Sprint 1 Completion Report

Including

Architecture

Component hierarchy

Workspace framework

Navigation

Reusable widgets

Theme

Layout

Responsiveness

Accessibility

Testing

Regression Summary

Known limitations

Future UI roadmap

==========================================================
EXIT CRITERIA
==========================================================

✓ Application shell complete

✓ Navigation framework complete

✓ Workspace framework complete

✓ Home workspace complete

✓ Sidebar complete

✓ Header complete

✓ Inspector complete

✓ Status bar complete

✓ Notification framework complete

✓ Session framework complete

✓ Progress framework complete

✓ Reusable widgets complete

✓ UI tests passing

✓ Backend regression tests passing

✓ No architecture violations

Finally

Commit

Push

Tag

v2-ui-foundation

Do NOT proceed to UI Sprint 2 until this framework is validated.
