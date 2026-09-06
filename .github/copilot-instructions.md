# Copilot Instructions for tictoc

## Project Description

tictoc is a typed Python timing utility package that provides timers, intervals, timestamps, speed estimation, and progress-aware logging.

## Scope

These instructions apply to the entire repository.

## Project Context

- This is a Python package with sources under src/tictoc.
- Keep backward compatibility for public imports and compatibility modules.
- Preserve public API behavior and formatting semantics when possible.

## Development Rules

- Prefer small, targeted changes.
- Keep code typed and add type annotations on public functions and classes.
- Do not break existing public APIs unless explicitly requested.
- Add or update tests under tests/ for behavior changes.
- Maintain style consistency with the existing codebase.
- Avoid heavy new dependencies unless clearly justified.

## Quality Checks

Before finalizing changes, run:

- pytest -q

## Verification and Alignment

- Keep CHANGELOG.md updated when behavior or interfaces change.
- Keep README.md and docs/ content aligned with code changes.
- Verify dependencies are correctly declared in pyproject.toml.
- Keep MANIFEST.in updated.

## Third-Party Licensing Workflow

Based on dependencies declared in pyproject.toml:

- Archive third-party licenses under licenses/third_party/packages/<package>/.
- Save at least one LICENSE file for each package.
- Save COPYING too when upstream provides it.
- Keep licenses/third_party/summary.tsv updated with columns:
  package, version, license_file, source_url.
- Keep THIRD_PARTY_NOTICES.md updated.
- Ensure MANIFEST.in includes these artifacts.

## Safety

- Do not run destructive git history operations.
- Ask for clarification before broad refactors when requirements are ambiguous.
