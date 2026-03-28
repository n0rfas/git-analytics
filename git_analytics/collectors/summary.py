from datetime import date
from typing import Optional, Set

from git_analytics.history import CommitContext


class CommitsSummaryCollector:
    name = "commits_summary"

    branch_name: Optional[str] = None
    date_first_commit: Optional[date] = None
    date_last_commit: Optional[date] = None
    total_number_commit: int = 0
    authors: Set[str] = set()

    def consume(self, ctx: CommitContext) -> None:
        if self.branch_name is None:
            self.branch_name = ctx.commit.repo.active_branch.name

        commit_date = ctx.committed_datetime.date()

        if self.date_first_commit is None or commit_date < self.date_first_commit:
            self.date_first_commit = commit_date

        if self.date_last_commit is None or commit_date > self.date_last_commit:
            self.date_last_commit = commit_date

        self.total_number_commit += 1
        if ctx.commit_author not in self.authors:
            self.authors.add(ctx.commit_author)

    def build_report(self) -> object:
        return {
            "branch_name": self.branch_name,
            "date_first_commit": self.date_first_commit,
            "date_last_commit": self.date_last_commit,
            "total_number_commit": self.total_number_commit,
            "total_authors": len(self.authors),
        }
