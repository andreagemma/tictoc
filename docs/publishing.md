# Publishing ga-tictoc to PyPI

The `Publish to PyPI` workflow builds, tests, verifies, and publishes both the
wheel and source distribution using PyPI Trusted Publishing.

No long-lived PyPI API token is stored in GitHub.

## One-Time PyPI Setup

The `ga-tictoc` name was not present on PyPI when this workflow was prepared.
Before the first publication, create a pending Trusted Publisher on PyPI:

1. Sign in to PyPI.
2. Open `Your projects` > `Publishing`.
3. Choose `Add a new pending publisher`.
4. Set project name to `ga-tictoc`.
5. Set owner to `andreagemma`.
6. Set repository name to `tictoc`.
7. Set workflow name to `publish-pypi.yml`.
8. Set environment name to `pypi`.

The values must match the workflow exactly.

## GitHub Environment

Create a GitHub environment named `pypi` under:

`Settings` > `Environments` > `New environment`

Optional protection rules can require approval before publication.

## Publishing a Release

Update the version in `pyproject.toml`, commit it, and create a matching tag:

```bash
git tag v0.2.0
git push origin main --tags
```

The existing `Release` workflow creates the GitHub release. When that workflow
finishes successfully, `Publish to PyPI` finds the latest stable release tag and
publishes its source.

Both workflows verify that the tag matches the version in `pyproject.toml`.

The workflow can also be started manually from GitHub Actions. PyPI does not
allow overwriting an existing version, so manual runs require a version that has
not already been published.

## Installing the Latest Release

```bash
python -m pip install --upgrade ga-tictoc
```

The distribution name is `ga-tictoc`, while the Python package remains:

```python
from tictoc import TicToc
```

The generated wheel is `py3-none-any`, so one wheel supports all operating
systems and every supported Python version. The project currently requires
Python 3.10 or newer.
