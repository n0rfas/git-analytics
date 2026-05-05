
The detailed analysis tool for git repositories - forked version from [here](https://github.com/n0rfas/git-analytics) with SQLite acting as the data store to provide better experience.

## Installation

The latest stable version can be installed directly from PyPI:

```sh
pip install git-analytics-sqlite
```

## Usage

Run from inside any git repository, then open [http://localhost:8000/](http://localhost:8000/) in your browser:

```sh
git-analytics-sqlite
```

On first launch the dashboard will show a **Scan repository** button. Click it to parse the git history and populate the local database. Subsequent launches load instantly from the cached data. Use the **Scan** button in the header at any time to pick up new commits.

### SQLite database

Commit data is stored in a per-repository SQLite database under your platform's user data directory:

| Platform | Location |
|----------|----------|
| Linux    | `~/.local/share/git-analytics/<repo>/<repo>_<hash>.db` |
| macOS    | `~/Library/Application Support/git-analytics/<repo>/<repo>_<hash>.db` |
| Windows  | `%APPDATA%\git-analytics\<repo>\<repo>_<hash>.db` |

The `<hash>` is a short fingerprint of the repository's full path, so two repositories with the same folder name never share a database.

Use the folder icon button in the header to open the database directory in your file manager.

### Custom database path

Pass `--db` to override the default location:

```sh
git-analytics-sqlite --db /path/to/my.db
```

## Screenshots

![screenshot 1](https://git-analytics.com/static/main_0_1_13.png)

## Development

### Installation

```bash
poetry install --with dev
```

### Running

```bash
poetry run git-analytics-sqlite
```

### Building

```bash
poetry build
# produces dist/git_analytics-<version>-py3-none-any.whl
```

Install the built wheel directly with pip:

```bash
pip install dist/git_analytics-*.whl
```

### Tests

```bash
poetry run pytest
poetry run pytest --cov=git_analytics --cov-report=term-missing --cov-fail-under=45
```

### Type Checking

```bash
poetry run mypy .
```

### Linting

```bash
poetry run ruff check .
poetry run ruff check --select I .
```
