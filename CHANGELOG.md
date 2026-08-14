# Changelog

All notable changes to DVA Platform are documented in this file.

## [2.0.2] — 2026-08-14

### Integration Audit — Release Readiness

Backend engines fully wired into the UI, stale UI tests updated, and a full integration audit completed.

#### Changed

- **Backend Engine Wiring**: `DetectionService -> DetectionEngine`, `CanonicalService -> CanonicalEngine`, `PreviewService -> CanonicalDataset`, `RequirementService -> RequirementLayer`, `ConnectionService -> LocalDataSource`, `ProcessingService -> ProcessingEngine`, `ValidationService -> ValidationEngine` — UI now exercises the real backend paths with empty-start fallbacks
- **Operation Service**: Execution steps and summary now source the real `OperationContext`
- **Processing Auto-Config**: `total_value` calculation no longer emitted when aggregation consumes raw quantity/price columns
- **UI Schema Alignment**: UI "sales" essential field aligned to backend "price" canonical schema
- **Test Fixtures**: Shared `tests/ui/conftest.py` fixtures; stale demo-data UI tests updated to empty-start + injected fixture data

#### Fixed

- **Test Runner**: Integration tests now carry the `integration` marker (auto-assigned by directory in root conftest); `scripts/run_all_tests.py` previously reported Integration FAILED because no tests were selected — now all 8 stages pass
- **Static Analysis**: Unused imports removed from 5 scripts (`environment_validation`, `run_all_tests`, `run_pat`, `startup_validation`, `generate_release_report`); pyflakes clean across the whole repo
- **Version Consistency**: App version bumped to `2.0.2` across `dav_platform/__init__.py`, home workspace, status bar, admin service, and migration metadata (previously 2.0.0 while CHANGELOG documented 2.0.1)
- **Dependency Alignment**: `pyarrow` and `duckdb` verified present in the environment

## [2.0.1] — 2026-07-22

### Hotfix Sprint — Release Readiness

Root-cause analysis and fixes for demo initialization failure, demo mode isolation, integration audit, UX clean-up, and silent error handling across all layers.

#### Fixed

- **Demo Initialization**: Five root causes fixed — empty workspace on demo start (demo CSVs now copied to `~/.dva/demo_temp/`), missing `context.current_connection_id` sync after connection creation, silent error swallowing in `start_demo()`, services not syncing current IDs from restored context, and demo datasets never loaded into detection/canonical/preview
- **Demo Mode Isolation**: All project/connection CRUD operations guarded during demo; amber "Demo Mode" banner in header; clean teardown on exit with no data leaks to production
- **Integration Audit**: 10 workspace `__init__.py` placeholder docstrings removed; home workspace dashboard now reads live `project_svc().list_projects()` instead of hardcoded list; execution summary widget reads live `proc_svc().results_summary`
- **Connection Manager**: All three connection types (Local, SSH, MFT) audited — all fields covered, Create/Edit/Delete/Duplicate/Test/Browse verified functional
- **Sidebar Clean-up**: Removed stale "downloads" and "history" nav entries that had no registered workspace implementations
- **Silent Exception Handlers**: 8 locations across detection engine, validation engine, flush cache, encoding detection, and Excel discovery upgraded from silent `except Exception: pass` to `logger.warning(..., exc_info=True)`
- **No-op Branch**: `Timer.__exit__` in performance service no longer discards elapsed time — logs at debug level when a label is set

## [2.0.0] — 2026-07-21

### UX Integration Sprint — Production Readiness

This release transforms DVA from "Architecture Complete" to "Production Ready" through focused work on UX, integration, stability, compatibility, documentation, and first-run experience.

#### Added

- **First-Run Welcome Wizard**: 7-step onboarding (Theme → Project → Connection → Detection → Mapping → Ready) with estimated completion time
- **Guided User Experience**: Every workspace now shows step guidance with purpose, instructions, required inputs, expected outputs, and next-step navigation
- **Dynamic Connection Manager**: Configurable forms for LOCAL, SSH, and MFT connection types with field-level validation
- **Demo Mode**: Isolated demo environment with 3 retailer sample datasets; clean teardown on exit
- **Theme System**: Expanded to 4 themes — Light, Dark, System, and High Contrast (accessibility)
- **Developer Mode**: 7-tab diagnostic panel showing backend/frontend status, context state, controllers, services, system resources, and streaming status
- **System Health Dashboard**: Real-time health monitoring with Healthy/Warning/Error badges for all subsystems
- **Performance Optimization**: PerformanceService with TTL-based caching, VirtualTable with pagination, LazyLoader for deferred rendering, and lazy workspace imports via importlib
- **Product Polish**: 20+ new CSS classes, reusable empty state/error dialog/loading overlay widgets, keyboard shortcuts manager, auto-dismiss notifications, and tooltips throughout
- **Documentation**: User Guide, Quick Start Guide, Administrator Guide, Developer Guide, Architecture Guide, Plugin Guide, Troubleshooting Guide, FAQ, Release Notes, Known Limitations, Future Roadmap, Compatibility Matrix, Installation Guide
- **Installation Tooling**: Dependency checker, environment validation, startup validation scripts
- **Test Infrastructure**: Release blocker regression tests (16 tests), consolidated test runner, Product Acceptance Test (PAT) script, release report generator
- **Dependency Management**: `requirements.txt` with pinned versions

#### Changed

- **Services**: All 5 core services (Project, Connection, Detection, Canonical, Preview) now start clean with no demo data seeding
- **Workspaces**: Detection reads real files from ConnectionService; Canonical reads real columns from DetectionService; Preview computes from real mappings; Settings and Help replaced placeholders with full implementations
- **Navigation**: Sidebar now dynamically enables/disables workspaces based on pipeline state (e.g., Detection locked until connection is active)
- **Theme Persistence**: Theme, sidebar state, window size, and splitter position persist across sessions via WorkspaceContext

#### Removed

- All demo/sample data from production services
- Placeholder workspaces (Settings, Help)
- Static connection types (replaced with dynamic form system)

#### Fixed

- Theme switching now properly persists across sessions
- Circular import in guidance_service.py resolved
- Workspace navigation correctly handles disabled states
