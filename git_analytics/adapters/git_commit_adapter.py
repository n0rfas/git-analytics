from git import Commit

from git_analytics.entities import AnalyticsCommit


def git_commit_to_analytics_commit(commit: Commit) -> AnalyticsCommit:
    return AnalyticsCommit(
        sha=commit.hexsha,
        commit_author=commit.author.name,
        committed_datetime=commit.committed_datetime,
        lines_insertions=commit.stats.total["insertions"],
        lines_deletions=commit.stats.total["deletions"],
        files_changed=commit.stats.total["files"],
        message=commit.summary.strip(),
    )
