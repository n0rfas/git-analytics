import pytest

from git_analytics.analyzers.language_statistics import _get_file_extension


@pytest.mark.parametrize(
    "file_path, expected_extension",
    [
        ("Dockerfile", "no_extension"),
        (".dockerignore", "no_extension"),
        ("folder/.env", "no_extension"),
        ("pyproject.toml", "toml"),
        ("src/web/main.py", "py"),
        ("index.HTML", "html"),
        ("src/style.CSS", "css"),
        ("app.dev.JS", "js"),
        ("tests/{test_data.py => test_fake_data.py}", "py"),
    ],
)
def test_commit_type_get_type_list(file_path, expected_extension):
    assert _get_file_extension(file_path) == expected_extension
