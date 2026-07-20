# Changelog

All notable changes to DVA Platform are documented in this file.

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
