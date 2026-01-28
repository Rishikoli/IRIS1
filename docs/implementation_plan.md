# Documentation Restructuring Plan

## Goal Description
Refactor the `docs/` directory to strictly match the user's requested 4 files:
1.  **System Design**
2.  **SDK API Reference**
3.  **Reference Agents**
4.  **Performance Report**

(We will also keep `SETUP.md` as it is critical for running the project, but we will focus on these 4).

## Proposed Changes

### Documentation

#### [NEW] [SYSTEM_DESIGN.md](file:///home/aditya/IRIS1/docs/SYSTEM_DESIGN.md)
- **Source**: Consolidate `docs/project_overview.md` and `docs/PROJECT_DOCUMENTATION.md`.
- **Content**: Architecture, Tech Stack, Data Flow.

#### [NEW] [SDK_API_REFERENCE.md](file:///home/aditya/IRIS1/docs/SDK_API_REFERENCE.md)
- **Source**: Rename `docs/sentiment_api.md`.
- **Content**: API endpoints, Request/Response formats.

#### [NEW] [REFERENCE_AGENTS.md](file:///home/aditya/IRIS1/docs/REFERENCE_AGENTS.md)
- **Source**: Extract "Council of Agents" sections from `docs/project_presentation.md` and `docs/project_overview.md`.
- **Content**: Table of agents, their roles, and descriptions.

#### [NEW] [PERFORMANCE_REPORT.md](file:///home/aditya/IRIS1/docs/PERFORMANCE_REPORT.md)
- **Source**: New file (recreating missing content based on context).
- **Content**: Intel VTune validation, performance metrics (placeholder/template).

#### [DELETE]
- `docs/project_overview.md`
- `docs/PROJECT_DOCUMENTATION.md`
- `docs/sentiment_api.md`
- `docs/project_presentation.md` (after extraction)
- `docs/ux_design.md` (Merge into System Design if needed, or delete if "down to md file we need" is strict). *Decision: Delete, merge key UX points into System Design.*

## Verification Plan

### Manual Verification
1.  Check that `docs/` contains only the requested files (plus `SETUP.md`).
2.  Verify `SYSTEM_DESIGN.md` contains the full architecture overview.
3.  Verify `REFERENCE_AGENTS.md` lists all agents correctly.
