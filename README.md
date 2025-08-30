# Git-Analytics

The detailed analysis tool for git repositories.

## Installation

The latest stable version can be installed directly from PyPI:

```sh
pip install git-analytics
```

## Usage

To run, enter the command and open the browser at [http://localhost:8000/](http://localhost:8000/).

```sh
git-analytics
```

## Screenshots

![screenshot 1](https://live.staticflickr.com/65535/52679528807_48caac329f_k.jpg)

![screenshot 2](https://live.staticflickr.com/65535/52680543193_c676158df2_k.jpg)

![screenshot 3](https://live.staticflickr.com/65535/52679528732_1f7b9351cd_k.jpg)

## Development

### Installation

```bash
poetry install --with dev
```

### Running

```bash
poetry run git-analytics
```

### Tests

```bash
poetry run pytest
poetry run pytest --cov=git_analytics --cov-report=term-missing       
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
