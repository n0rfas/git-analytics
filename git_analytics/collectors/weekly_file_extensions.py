from typing import Dict
from pathlib import Path
from git_analytics.history import CommitContext
from ._base import WeeklyCollector


def _get_file_extension(file_path: str) -> str:
    """Извлекает расширение файла из пути."""
    path = Path(file_path)
    extension = path.suffix

    if not extension:
        return "(no extension)"

    return extension.lower()


class WeeklyFileExtensionsCollector(WeeklyCollector):
    """
    Коллектор для подсчета изменений строк кода по расширениям файлов на недельной основе.

    Формат данных:
    {
        "26W12": {".py": 150, ".js": -20, ".md": 50},
        "26W13": {".py": 200, ".ts": 100}
    }

    Где ключ - это год и номер недели (формат: ГГWНН),
    а значение - словарь с расширениями и количеством строк (положительное - добавлено, отрицательное - удалено).
    """

    name = "weekly_file_extensions"

    def _aggregate_commit(self, week_key: str, ctx: CommitContext) -> None:
        """
        Агрегирует данные коммита для конкретной недели.

        Для каждого файла в коммите:
        - Извлекает расширение файла
        - Подсчитывает чистое изменение строк (добавления - удаления)
        """
        commit = ctx.commit

        # Получаем статистику по файлам из коммита
        if hasattr(commit.stats, "files"):
            for file_path, file_stats in commit.stats.files.items():
                extension = _get_file_extension(file_path)

                # Подсчитываем чистое изменение: добавления - удаления
                insertions = file_stats.get("insertions", 0)
                deletions = file_stats.get("deletions", 0)
                net_change = insertions - deletions

                # Добавляем данные в формате: {extension: net_change}
                self._weeks_data[week_key].append({extension: net_change})

    def build_report(self) -> Dict[str, Dict[str, int]]:
        """
        Строит итоговый отчет, суммируя изменения по расширениям для каждой недели.

        Returns:
            Dict[str, Dict[str, int]]: Словарь вида {week_key: {extension: total_lines}}
        """
        raw = super().build_report()

        result = {}
        for week_key, changes_list in raw.items():
            extensions_total: Dict[str, int] = {}

            # Суммируем все изменения для каждого расширения
            for change_dict in changes_list:
                for extension, net_change in change_dict.items():
                    if extension in extensions_total:
                        extensions_total[extension] += net_change
                    else:
                        extensions_total[extension] = net_change

            result[week_key] = extensions_total

        return result
