from wsgiref.simple_server import make_server

from git import Repo

from git_analytics.adapters import git_commit_to_analytics_commit
from git_analytics.analyzers import (
    AuthorsStatisticsAnalyzer,
    CommitAnalyticsRunner,
    CommitTypeAnalyzer,
    HistoricalStatisticsAnalyzer,
    LinesAnalyzer,
)
from git_analytics.web_app import create_web_app


def run():
    repo = Repo()

    runner = CommitAnalyticsRunner(
        analyzers=[
            AuthorsStatisticsAnalyzer(),
            HistoricalStatisticsAnalyzer(),
            LinesAnalyzer(),
            CommitTypeAnalyzer(),
        ]
    )

    print("Starting analytics...")
    # Iterate through all commits in the repository
    for commit in repo.iter_commits():
        analytics_commit = git_commit_to_analytics_commit(commit)
        runner.feed(analytics_commit)
    print("Analytics completed.")

    data = runner.collect()
    data["about"] = {
        "url_repository": repo.remotes.origin.url,
        "branch_name": repo.active_branch.name,
        "date_first_commit": str(repo.head.commit.committed_datetime),
        "date_last_commit": str(repo.head.commit.committed_datetime),
        "total_number_commit": len(list(repo.iter_commits())),
    }

    web_app = create_web_app(data=data)

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
