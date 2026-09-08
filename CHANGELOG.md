# Changelog

All notable changes to this project will be documented in this file.

## 0.2.4 - 2026-09-08

- Restored the PyPI publish workflow file name to `publish-pypi.yml` so PyPI
  Trusted Publishing matches the configured GitHub workflow again.

## 0.2.2 - 2026-09-08

- Aligned GitHub Actions workflows with the configreader flow and analogous file names:
  - `all.yml`
  - `ci.yml`
  - `fast_ci.yml`
  - `quality.yml`
  - `create-release.yml`
  - `create-release-whl.yml`
  - `release.yml`
- Removed legacy non-analog workflow files (`package.yml`, `publish-pypi.yml`).
- Bumped package/build version from `0.2.1` to `0.2.2`.

## 0.2.1 - 2026-09-06

- Added third-party compliance artifacts derived from dependencies declared in `pyproject.toml`:
  - `licenses/third_party/packages/<package>/LICENSE`
  - `licenses/third_party/summary.tsv`
  - `THIRD_PARTY_NOTICES.md`
- Updated `MANIFEST.in` to include third-party notices and archived license files in source distributions.
- Added repository Copilot instructions in `.github/copilot-instructions.md` aligned to project structure and quality checks.
- Updated package version to `0.2.1` in both `pyproject.toml` and `src/tictoc/__init__.py`.
