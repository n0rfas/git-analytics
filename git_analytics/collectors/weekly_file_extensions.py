from pathlib import Path
from typing import Dict

from git_analytics.history import CommitContext

from ._base import WeeklyCollector


def _get_file_extension(file_path: str) -> str:
    path = Path(file_path)
    extension = path.suffix

    if not extension:
        return "(no extension)"

    return extension.lower()


class WeeklyFileExtensionsCollector(WeeklyCollector):
    name = "weekly_file_extensions"

    def _aggregate_commit(self, week_key: str, ctx: CommitContext) -> None:
        commit = ctx.commit

        if hasattr(commit.stats, "files"):
            for file_path, file_stats in commit.stats.files.items():
                extension = _get_file_extension(file_path)

                insertions = file_stats.get("insertions", 0)
                deletions = file_stats.get("deletions", 0)
                net_change = insertions - deletions

                self._weeks_data[week_key].append({extension: net_change})

    def build_report(self) -> Dict[str, Dict[str, int]]:
        raw = super().build_report()

        result = {}
        for week_key, changes_list in raw.items():
            extensions_total: Dict[str, int] = {}

            for change_dict in changes_list:
                for extension, net_change in change_dict.items():
                    if extension in extensions_total:
                        extensions_total[extension] += net_change
                    else:
                        extensions_total[extension] = net_change

            result[week_key] = extensions_total

        return result
