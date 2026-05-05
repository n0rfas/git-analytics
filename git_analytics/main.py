import argparse
import os
from pathlib import Path
from wsgiref.simple_server import make_server

from git_analytics.analyzers import (
    AuthorsStatisticsAnalyzer,
    CommitsSummaryAnalyzer,
    CommitTypeAnalyzer,
    HistoricalStatisticsAnalyzer,
    LanguageAnalyzer,
    LinesAnalyzer,
)
from git_analytics.engine import CommitAnalyticsEngine, FileAnalyticsEngine
from git_analytics.sources import SqliteCommitSource, repo_db_path
from git_analytics.web_app import create_web_app


def make_analyzers():
    return [
        AuthorsStatisticsAnalyzer(),
        CommitsSummaryAnalyzer(),
        CommitTypeAnalyzer(),
        HistoricalStatisticsAnalyzer(),
        LanguageAnalyzer(),
        LinesAnalyzer(),
    ]


def run():
    parser = argparse.ArgumentParser(prog="git-analytics")
    parser.add_argument(
        "--db",
        metavar="PATH",
        help="path to SQLite database (default: user data directory)",
    )
    args = parser.parse_args()

    path_repo = os.getenv("PATH_REPO", ".")
    db_path = Path(args.db) if args.db else repo_db_path(path_repo)

    repo = _try_get_repo(path_repo)
    additional_data = _build_additional_data(repo)

    engine = CommitAnalyticsEngine(
        source=SqliteCommitSource(db_path),
        analyzers_factory=make_analyzers,
        additional_data=additional_data,
    )

    web_app = create_web_app(engine=engine, db_path=db_path, repo=repo)

    with make_server("", 8000, web_app) as httpd:
        print("Web service started at http://localhost:8000/")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping by Ctrl+C...")
        finally:
            httpd.server_close()
            print("Web service stopped")


def _try_get_repo(path: str):
    try:
        from git import InvalidGitRepositoryError, Repo
        return Repo(path)
    except Exception:
        return None


def _build_additional_data(repo):
    data = {}
    if repo is not None:
        try:
            data["name_branch"] = repo.active_branch.name
        except Exception:
            pass
    try:
        data["extension_stats"] = FileAnalyticsEngine().run()
    except Exception:
        pass
    return data


if __name__ == "__main__":
    run()
