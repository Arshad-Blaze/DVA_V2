# DVA Platform v2

Retail Data Processing Platform.

## Architecture

```
Data Access → Detection → Canonical → Requirement → Operation → Processing → Validation → Reporting → Cleanup
```

## Project Structure

```
dav_platform/
  core/          # Contracts and shared types
  connection/    # Data Access layer (Sprint 1)
  detection/     # Detection layer (Sprint 2)
  canonical/     # Canonical layer (Sprint 3)
  requirements/  # Requirement layer (Sprint 4)
  operations/    # Operation layer (Sprint 5)
  processing/    # Processing layer (Sprint 6)
  validation/    # Validation layer (Sprint 7)
  reporting/     # Reporting layer (Sprint 8)
  cleanup/       # Cleanup layer (Sprint 9)
  workflow/      # Workflow orchestration
  ui/            # User interface (LAST)
  shared/        # Shared utilities
```

## Engineering Rules

- Architecture drives code
- No layer bypasses
- Streaming First
- Polars First
- Composition over inheritance
- Small modules, small functions
- Strong typing
- High cohesion, low coupling

## Testing

```bash
python3 -m pytest tests/unit/ -v
```
