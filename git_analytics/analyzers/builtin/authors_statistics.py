from collections import defaultdict
from dataclasses import asdict
from typing import Dict

from git_analytics.entities import AnalyticsCommit, AuthorStatistics


class AuthorsStatisticsAnalyzer:
    name = "authors_statistics"

    def __init__(self) -> None:
        self._dict_authors = defaultdict(AuthorStatistics)

    def update(self, c: AnalyticsCommit) -> None:
        author_name = c.commit_author

        self._dict_authors[author_name].commits += 1
        self._dict_authors[author_name].insertions += c.lines_insertions
        self._dict_authors[author_name].deletions += c.lines_deletions

    def result(self) -> Dict[str, int]:
        data = dict(
            sorted(
                self._dict_authors.items(),
                key=lambda item: item[1].commits,
                reverse=True,
            )
        )
        return {author: asdict(achievements) for author, achievements in data.items()}
