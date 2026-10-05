# Repository Guidelines

## Response Guidelines
- Respond concisely. Skip pleasantries, preambles, and unnecessary explanations.
Provide only the code or direct answer requested.
- When grilling, ask one question at a time and wait for a response before proceeding.

## Project Overview
A map-making tool that generates a route of a requested distance and shape
(perfect square, equilateral triangle, right triangle) starting from a
user-supplied coordinate. MVP routes are for walking/running.

v1 scope: a CLI that accepts a start point, target distance, and shape, and
writes a GeoJSON file. No web UI. Route geometry should follow actual
walkable/runnable streets, trails, and paths while excluding highways.

## Tech Stack
- Language: Python (target 3.11+)
- Tooling: `uv` (dependency management, virtualenvs, running scripts)
- Route engine: `networkx` with `osmnx` for OpenStreetMap-backed travel
  networks.
- Output format: GeoJSON

## Project Structure
- `src/routegen/` — package source. Keep concerns separated:
  - `graph/` — graph construction and loading
  - `routing/` — path generation, distance/shape constraints
  - `io/` — GeoJSON serialization, file reading/writing
  - `cli.py` — command-line entry point
- `tests/` — mirrors `src/` structure (e.g. `tests/routing/test_loop.py`)
- `assets/` — static data (sample graphs, fixtures, small GeoJSON samples)
- `docs/` — design notes
  - `docs/adr/` — architecture decision records
- `GLOSSARY.md` — domain terms (start point, shape, target distance, etc.)

## Commands
- Install deps: `uv sync`
- Add a dependency: `uv add <package>`
- Run tests: `uv run pytest`
- Run linter: `uv run ruff check`
- Run formatter: `uv run ruff format`
- Run CLI: `uv run routegen --start <lat,lon> --distance <meters> --shape <shape> --output <file.geojson>`

Update this section whenever tooling changes.

## Coding Style
- Follow PEP 8. `ruff` handles formatting and linting — run it before any commit.
- `snake_case` for functions, variables, and modules. `PascalCase` for classes.
- Type hints on all public functions.
- Prefer small, focused modules over large files.
- Keep map/routing concerns free of I/O. I/O lives in `io/` and `cli.py`.

## Testing
- Use `pytest`.
- Test files mirror source layout: `tests/routing/test_loop.py` tests
  `src/routegen/routing/loop.py`.
- Every ticket must add or update tests for the behavior it introduces.
- Prefer deterministic tests over timing- or network-dependent ones. Use
  synthetic fixtures for routing behavior, and isolate live OSM access behind
  graph-loading boundaries.

## Git & PRs
- Branch naming: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`.
- Commit messages: short, imperative. `Add loop generator`, `Validate GeoJSON
  output`. One logical change per commit.
- Never commit directly to `main`.
- PRs include: summary, testing notes, and a sample GeoJSON for any change
  that alters route output.
- Link the GitHub Issue the PR closes.

## Workflow (agentic process)
This repo follows a strict pipeline. Do not skip stages.

1. **Grill** — clarify requirements through Q&A. No code.
2. **Spec** — write the PRD/design into `docs/`. No code.
3. **Tickets** — break the spec into GitHub Issues, each small enough to fit
   in one fresh agent session (roughly one file of change, plus tests).
4. **Implement** — one ticket per session. Start from a clean context. Read
   only the files the ticket names. Write tests first where practical.
5. **Review** — run `ruff check`, `ruff format`, and `pytest` before opening
   a PR.

Rules:
- No implementation work begins without a corresponding GitHub Issue.
- One ticket per context window. Clear context between tickets; do not
  "compact" across tickets.
- If a ticket is too large to finish in one session, stop and split it.
- Keep `agents.md` lean. Deep design docs belong in `docs/`, not here.

## Agent skills

### Issue tracker

Issues live in GitHub Issues, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `GLOSSARY.md` plus `docs/adr/`. See `docs/agents/domain.md`.

## Agent-Specific Instructions
- Inspect the current tree before editing. Do not overwrite user-created files.
- Keep edits scoped to the ticket. No drive-by refactors.
- If the ticket is ambiguous, stop and ask rather than guessing.
- Update this file whenever real tooling, directories, or workflows change.
