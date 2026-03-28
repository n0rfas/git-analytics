from git_analytics.engines.metrics import CommitContext


class AuthorCommitsCounter:
    name = "authors_statistics"
    authors = {}

    def consume(self, ctx: CommitContext) -> None:
        if ctx.commit_author not in self.authors:
            self.authors[ctx.commit_author] = {}
            self.authors[ctx.commit_author]["commits"] = 0
            self.authors[ctx.commit_author]["insertions"] = 0
            self.authors[ctx.commit_author]["deletions"] = 0

        self.authors[ctx.commit_author]["commits"] += 1
        self.authors[ctx.commit_author]["insertions"] += ctx.commit.stats.total["insertions"]
        self.authors[ctx.commit_author]["deletions"] += ctx.commit.stats.total["deletions"]

    def build_report(self) -> object:
        return self.authors
