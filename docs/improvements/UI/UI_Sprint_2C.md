You are continuing the DVA Platform v2 rebuild.

IMPORTANT

This is UI Sprint 2.5 — Persistence Foundation & Workspace Context.

UI Sprint 1 and UI Sprint 2 are COMPLETE.

DO NOT redesign the UI.

DO NOT modify the backend.

DO NOT change frozen workspace architecture.

This sprint exists ONLY to replace temporary in-memory storage with a persistent foundation before additional workspaces are implemented.

==========================================================
OBJECTIVE
==========================================================

Introduce a persistence layer for the UI.

The UI should survive:

Application restart

Browser refresh

Workspace switching

Future project growth

This sprint is infrastructure only.

No new business features.

==========================================================
WHY THIS EXISTS
==========================================================

Current implementation stores:

Projects

Connections

Session

Navigation

Recent Projects

only in memory.

This becomes difficult to maintain as Detection, Canonical, Processing and Validation begin storing configuration.

Build persistence NOW before more workspaces depend on temporary state.

==========================================================
TARGET ARCHITECTURE
==========================================================

UI

↓

Workspace

↓

Controller

↓

Service

↓

Persistence Service

↓

Storage Backend

No workspace should read/write files directly.

==========================================================
CREATE
==========================================================

ui/

    services/

        persistence_service.py

        storage_service.py

        serialization_service.py

        workspace_context.py

        migration_service.py

==========================================================
PERSISTENCE SERVICE
==========================================================

Responsibilities

Save objects

Load objects

Delete objects

Backup

Restore

Version metadata

Atomic writes

Graceful recovery

Never expose filesystem details.

==========================================================
STORAGE BACKEND
==========================================================

Initially support

JSON

Design so SQLite can be added later without changing services.

Follow Repository Pattern.

==========================================================
SERIALIZATION
==========================================================

Support serialization for

Project

Connection

Navigation History

Session Preferences

Theme

Workspace State

Recent Projects

Recent Connections

Future workspace configurations

Avoid duplicated serialization logic.

==========================================================
PROJECT STORAGE
==========================================================

Persist

Project metadata

Description

Directories

Retailer

Created

Modified

Status

Tags

Version

Recent execution

Project should survive restart.

==========================================================
CONNECTION STORAGE
==========================================================

Persist

Connection profiles

Connection type

Directory

Description

Favorites

Recent connections

Connection preferences

Do NOT store sensitive credentials in plain text.

Design credential abstraction for future secure storage.

==========================================================
WORKSPACE CONTEXT
==========================================================

Create a WorkspaceContext object.

It should become the shared UI context.

Suggested fields

Current Project

Current Connection

Current Workspace

Current Detection Session

Current Canonical Session

Current Execution

Navigation History

User Preferences

Theme

Notifications

Selection

This becomes the single UI state object.

==========================================================
SESSION LIFECYCLE
==========================================================

Support

Load previous session

Restore workspace

Restore project

Restore navigation

Restore preferences

Clean shutdown

==========================================================
DIRECTORY STRUCTURE
==========================================================

Create standard application storage.

Example

~/.dva/

    projects/

    settings/

    cache/

    history/

    sessions/

    backups/

    logs/

    metadata/

Platform independent.

==========================================================
BACKUP
==========================================================

Support

Automatic backup

Manual backup

Restore backup

Corruption recovery

==========================================================
MIGRATION
==========================================================

Support persistence versioning.

Example

Storage Version

Application Version

Migration Version

Future schema migrations should be automatic.

==========================================================
HOME WORKSPACE
==========================================================

Update Home.

Display

Recent Projects

Last Opened

Pinned Projects

Resume Previous Session

Restore Last Workspace

==========================================================
PROJECT WORKSPACE
==========================================================

Update

Projects should now load from persistence.

CRUD operations should persist automatically.

==========================================================
CONNECTION WORKSPACE
==========================================================

Update

Connections should persist.

Recent connections should persist.

Favorites should persist.

==========================================================
WORKSPACE STATE
==========================================================

Persist

Expanded panels

Selected tabs

Filters

Sort order

Inspector visibility

Sidebar state

Theme

==========================================================
DESIGN PRINCIPLES
==========================================================

Repository Pattern

Single Responsibility

Dependency Injection

No UI File Access

No Duplicate Serialization

Future Database Ready

==========================================================
NON NEGOTIABLE
==========================================================

Workspaces never touch files.

Controllers never serialize.

Services never render UI.

Persistence layer owns storage.

==========================================================
TESTING
==========================================================

Create tests for

Persistence

Serialization

Migration

Workspace Context

Backup

Restore

Corrupted JSON

Missing files

Atomic writes

Version migration

Project persistence

Connection persistence

Session restore

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
ARCHITECTURE REVIEW
==========================================================

Verify

No workspace accesses filesystem.

No controller accesses filesystem.

All persistence through PersistenceService.

WorkspaceContext becomes the single shared UI context.

Project and Connection workspaces remain isolated.

No backend coupling introduced.

==========================================================
DELIVERABLES
==========================================================

Produce

UI Sprint 2.5 Completion Report

Including

Persistence Architecture

Repository Design

Workspace Context

Serialization Model

Storage Layout

Session Lifecycle

Backup Strategy

Migration Strategy

Testing Summary

Regression Summary

Known Limitations

Future Enhancements

==========================================================
EXIT CRITERIA
==========================================================

✓ Persistence service complete

✓ Storage backend complete

✓ Serialization complete

✓ WorkspaceContext complete

✓ Project persistence complete

✓ Connection persistence complete

✓ Session restore complete

✓ Backup complete

✓ Migration framework complete

✓ UI tests passing

✓ Backend regression passing

✓ Architecture review passed

✓ No filesystem access outside persistence layer

Commit

Push

Tag

v2-ui-persistence-foundation

Freeze UI Sprint 2.5

Write Completion Report
