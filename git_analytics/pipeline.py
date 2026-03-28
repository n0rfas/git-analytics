from .snapshot import CodebaseSnapshot
from .history import GitHistoryWalker
from .engine import MetricsEngine
from .collectors import (
    AuthorCommitsCounter,
    CommitTypeCollector,
    CommitsSummaryCollector,
    CodeChurnCollector,
    WeeklyFileExtensionsCollector,
)
from .insights import BusFactorInsight, WeeklyLinesHistory


def run_analytics_pipeline(repo_path: str = ".", days: int = 365):
    # snapshot
    codebase = CodebaseSnapshot(repo_path).run()

    # collection
    history = GitHistoryWalker(path=repo_path, since_days=days)
    collectors = [
        AuthorCommitsCounter(),
        CodeChurnCollector(),
        CommitsSummaryCollector(),
        CommitTypeCollector(),
        WeeklyFileExtensionsCollector(),
    ]
    activity = MetricsEngine(history, collectors).run()

    # insights
    result = {
        "bus_factor": BusFactorInsight(activity).compute(),
        "weekly_lines_history": WeeklyLinesHistory(codebase, activity).compute(),
        "commits_summary": activity["commits_summary"],
        "commit_type": activity["commit_type"],
        "code_churn_21d": {
            "churn_ratio": activity["code_churn_21d"]["churn_ratio"],
            "added_lines_in_period": activity["code_churn_21d"]["added_lines_in_period"],
            "short_lived_deleted_lines": activity["code_churn_21d"]["short_lived_deleted_lines"],
        },
    }

    return result
