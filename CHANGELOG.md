# Changelog

All notable changes to this project will be documented in this file.

## 0.2.1 - 2026-09-06

- Added third-party compliance artifacts derived from dependencies declared in `pyproject.toml`:
  - `licenses/third_party/packages/<package>/LICENSE`
  - `licenses/third_party/summary.tsv`
  - `THIRD_PARTY_NOTICES.md`
- Updated `MANIFEST.in` to include third-party notices and archived license files in source distributions.
- Added repository Copilot instructions in `.github/copilot-instructions.md` aligned to project structure and quality checks.
- Updated package version to `0.2.1` in both `pyproject.toml` and `src/tictoc/__init__.py`.
