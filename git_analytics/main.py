from wsgiref.simple_server import make_server

from git import InvalidGitRepositoryError, Repo

from git_analytics.analyzers import (
    AuthorsStatisticsAnalyzer,
    CommitsSummaryAnalyzer,
    CommitTypeAnalyzer,
    HistoricalStatisticsAnalyzer,
    LinesAnalyzer,
)
from git_analytics.engine import CommitAnalyticsEngine
from git_analytics.sources import GitCommitSource
from git_analytics.web_app import create_web_app


def make_analyzers():
    return [
        AuthorsStatisticsAnalyzer(),
        CommitsSummaryAnalyzer(),
        CommitTypeAnalyzer(),
        HistoricalStatisticsAnalyzer(),
        LinesAnalyzer(),
    ]


def run():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        print("Error: Current directory is not a git repository.")
        return

    engine = CommitAnalyticsEngine(
        source=GitCommitSource(repo),
        analyzers_factory=make_analyzers,
    )

    web_app = create_web_app(engine=engine)

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


if __name__ == "__main__":
    run()
