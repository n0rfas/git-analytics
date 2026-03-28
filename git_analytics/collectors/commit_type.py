from typing import List, Dict
from git_analytics.history import CommitContext
from ._base import WeeklyCollector


LIST_OF_TYPE_COMMIT: List[str] = ["feature", "fix", "docs", "style", "refactor", "test", "chore", "wip", "merge"]


def _get_type_list(commit_message: str) -> List[str]:
    result = [tag for tag in LIST_OF_TYPE_COMMIT if tag in commit_message.lower()]
    if result:
        return result
    return ["unknown"]


class CommitTypeCollector(WeeklyCollector):
    name = "commit_type"

    def _aggregate_commit(self, week_key: str, ctx: CommitContext) -> None:
        commit_message = ctx.commit.message
        commit_types = _get_type_list(commit_message)

        for commit_type in commit_types:
            self._weeks_data[week_key].append(commit_type)

    def build_report(self) -> Dict[str, Dict[str, int]]:
        raw = super().build_report()

        result = {}
        for week, types_list in raw.items():
            types_count: Dict[str, int] = {}
            for commit_type in types_list:
                types_count[commit_type] = types_count.get(commit_type, 0) + 1

            result[week] = types_count

        return result
